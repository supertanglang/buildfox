#!/usr/bin/python3

import os
import sys
import json
import glob
import argparse
import traceback
from pprint import pprint
from deepdiff import DeepDiff # pip install deepdiff

sys.path.append("..")
from lib_parser import parse
from lib_engine import Engine

class EngineMock:
	def __init__(self):
		self.output = []

	def fix_assigns(self, assign):
		return [list(t) for t in assign]

	def on_empty_lines(self, lines):
		self.output.append({
			"empty_lines": lines
		})

	def on_comment(self, comment):
		self.output.append({
			"comment": comment
		})

	def on_rule(self, obj, assigns):
		self.output.append({
			"rule": obj,
			"assigns": self.fix_assigns(assigns)
		})

	def on_build(self, obj, assigns):
		self.output.append({
			"build": obj[2],
			"targets_explicit": obj[0],
			"targets_implicit": obj[1],
			"inputs_explicit": obj[3],
			"inputs_implicit": obj[4],
			"inputs_order": obj[5],
			"assigns": self.fix_assigns(assigns)
		})

	def on_default(self, obj):
		self.output.append({
			"default": obj
		})

	def on_pool(self, obj, assigns):
		self.output.append({
			"pool": obj,
			"assigns": self.fix_assigns(assigns)
		})

	def filter(self, obj):
		self.output.append({
			"filter": [list(t) for t in obj]
		})

	def on_auto(self, obj, assigns):
		self.output.append({
			"auto": obj[1],
			"outputs": obj[0],
			"inputs": obj[2],
			"assigns": self.fix_assigns(assigns)
		})

	def on_print(self, obj):
		self.output.append({
			"print": obj
		})

	def on_assign(self, obj):
		self.output.append({
			"assign": list(obj)
		})

	def on_transform(self, obj):
		self.output.append({
			"transform": obj[0],
			"pattern": obj[1]
		})

	def on_include(self, obj):
		self.output.append({
			"include": obj
		})

	def on_subninja(self, obj):
		self.output.append({
			"subninja": obj
		})

def run_test(test_filename, print_json = False, print_ninja = False):
	print("-> Testing %s" % test_filename)
	try:
		with open(os.path.splitext(test_filename)[0] + ".json", "r") as f:
			reference = json.loads(f.read())
		engine = EngineMock()
		parse(engine, test_filename)
		if print_json:
			print("--- JSON ---------------------")
			print(json.dumps(engine.output, sort_keys = True, indent = "\t"))
			print("--- JSON END -----------------")
		diff = DeepDiff(reference, engine.output)
		if diff:
			print("Results differ from reference:")
			pprint(diff)
			return False

		with open(os.path.splitext(test_filename)[0] + ".ninja", "r") as f:
			reference = f.read()
		engine = Engine()
		engine.load(test_filename, logo = False)
		if print_ninja:
			print("--- NINJA --------------------")
			print(engine.text())
			print("--- NINJA END ----------------")
		diff = DeepDiff(reference, engine.text())
		if diff:
			print("Results differ from reference:")
			pprint(diff)
			return False

		return True
	except:
		err = sys.exc_info()[0]
		print("Exception error: %s" % err)
		traceback.print_exc()
		return False

argsparser = argparse.ArgumentParser(description = "buildfox test suite")
argsparser.add_argument("-i", "--in", help = "Test inputs", default = "suite/*.fox")
argsparser.add_argument("--dry", action = "store_true",
	help = "Ignore tests failures", default = False, dest = "dry")
argsparser.add_argument("--json", action = "store_true",
	help = "Print json output from parser", default = False, dest = "json")
argsparser.add_argument("--ninja", action = "store_true", help = "Print ninja output from engine", default = False, dest = "ninja")
argsparser.add_argument("--fail-fast", action = "store_true",
	help = "Abort after first failure", default = False, dest = "failfast")
args = vars(argsparser.parse_args())

# TODO clean up temporary ninja files in current working dir

results = []
for test_filename in glob.glob(args.get("in")):
	result = run_test(test_filename.replace("\\", "/"), args.get("json"), args.get("ninja"))
	results.append(result)
	if args.get("failfast") and not result:
		break

if not all(results):
	print("One or more tests failed")
	if not args.get("dry"):
		sys.exit(1)
else:
	print("All tests done.")