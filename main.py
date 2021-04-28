import os
import shutil
import toml
import requests
import markdown
import git
from jinja2 import Template

style = """
<style>
	body {
		margin: auto 200px auto;
		background: #30363d;
		font-size: 1.1em;
		color: white;
		font-family: monospace;
	}
	h3 {
		display: inline-block;
	}
	em {
		font-size: 0.7em;
	}
	a:any-link {
		color: inherit;
	}
	summary::marker {
		cursor: crosshair;
	}
	@media screen and (max-width: 600px) {
		body {
			margin: 10px;
		}
	}
	summary:focus {
		outline: none;
		border: none;
	}
	summary, .noselect {
		outline: none;
		border: none;
		-webkit-touch-callout: none; /* iOS Safari */
			-webkit-user-select: none; /* Safari */
			-khtml-user-select: none; /* Konqueror HTML */
				-moz-user-select: none; /* Old versions of Firefox */
					-ms-user-select: none; /* Internet Explorer/Edge */
							user-select: none; /* Non-prefixed version, currently
																		supported by Chrome, Edge, Opera and Firefox */
	}
</style>
"""

def copytree(src, dst, symlinks=False, ignore=None):
	for item in os.listdir(src):
		if item == "build":
			continue
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)

os.system('git submodule update --recursive --force --init')

if os.path.isdir('build'):
	shutil.rmtree('build')
os.mkdir('build')
copytree('.', 'build')
os.chdir('build')


data = toml.load('site.toml')

with open("netlify.toml.template", 'r') as configfile:
	template = Template(configfile.read())
	out = template.render(projects = data['project'])

with open("netlify.toml", 'a') as configfile:
	configfile.write(out)

domains = []
for project in data['project']:
	if 'gh' in project and not os.path.isdir('src/' + project['src']):
		git.Git('src').clone(project["gh"])
	domains.append(project['src'] + ".school.colewilson.xyz")

if 'TOKEN' in os.environ:
	site_id = os.environ['SITE_ID']
	token = os.environ['TOKEN']
	call = requests.put(
		"https://api.netlify.com/api/v1/sites/" + site_id,
		data={"domain_aliases": domains},
		headers={"Authorization": "Bearer " + token}
	)
	if call.status_code != 200:
		exit('API Call did not return a 200 status')

with open("index.html", 'r') as index:
	template = Template(index.read())
	out = template.render(projects = data['project'], pages = os.listdir('pages'), style=style)

with open("index.html", 'w+') as index:
	index.write(out)

for file in os.listdir('pages'):
	if file.endswith('.md'):
		with open('pages/' + file) as f:
			d = f.read()
		with open('pages/' + file, 'w+') as f:
			f.write(style if "<nocss></nocss>" not in d else "")
			f.write(markdown.markdown(d))
		plain = file[:-3]
		os.mkdir('pages/' + plain)
		os.rename('pages/' + file, 'pages/' + plain  + "/index.html")
