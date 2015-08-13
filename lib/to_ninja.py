# ------------------------------------ ninja generator tool

from lib.maskfile import to_esc_iter

def to_string(ir, args = None):
	variation = args["variation"]
	output = "# generated"

	output += "\n\n" + "\n".join([str(v) for k, v in ir.rules.items()]) if len(ir.rules) else ""
	output += "\n\n" + "\n".join([str(v) for v in ir.builds]) if len(ir.builds) else ""

	output += "\n\n"
	for prj_name, project in ir.projects.items():
		for name, paths in project.variations.items():
			target_name = prj_name + "_" + name
			output += "build " + target_name + ": phony " + " ".join(to_esc_iter(paths)) + "\n"
			if (not variation) or (name == variation):
				output += "default " + target_name + "\n"

	return output

def to_file(filename, ir, args = None):
	with open(filename, "w") as f:
		f.write(to_string(ir, args))
