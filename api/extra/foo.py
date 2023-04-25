i = 1
with open('tmp.py', 'w') as t:
	with open('admin.py', 'r') as a:
		for line in a:
			if "import csv" in line:
				continue
			if "rom django.utils.encoding import smart_str" in line:
				continue
			if "short_description" in line:
				t.write('export_csv'+str(i)+'.short_description = u"Export as CSV"\n')
				i += 1
			else:
				t.write(line)