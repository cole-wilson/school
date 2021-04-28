import os
import shutil
import toml
import requests
import json
from jinja2 import Template

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

os.system('git submodule update --recursive --force')

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
	domains.append(project['src'] + ".school.colewilson.xyz")

site_id = ""
token = ""
call = requests.put(
	f"https://api.netlify.com/api/v1/sites/{site_id}",
	data={"domain_aliases": domains},
	headers={"Authorization": f"Bearer {token}"}
)
