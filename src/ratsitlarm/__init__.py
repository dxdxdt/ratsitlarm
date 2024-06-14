import copy
import json
import os
import sys
from typing import Any
import pyjson5
import requests
import boto3


def loadConf () -> dict[str, Any]:
	with open("config.jsonc") as f:
		return pyjson5.load(f)

def dumpToStream (doc, s):
	s.write(json.dumps(doc, indent = '\t', ensure_ascii = False))
	s.write(os.linesep)

def doAWSSNS (r, doc):
	s = boto3.session.Session(
		profile_name = r.get("profile"),
		region_name = r.get("region")
	)
	c = s.client("sns")

	c.publish(
		TopicArn = r["topic"],
		Subject = r.get("subject", "Ratsitlarm hit"),
		Message = json.dumps(doc, indent = '\t', ensure_ascii = False)
	)

def disableAWSEvent (e):
	s = boto3.session.Session(
		profile_name = e.get("profile"),
		region_name = e.get("region")
	)
	c = s.client("events")

	c.disable_rule(Name = e["rule"], EventBusName = e.get("bus", "default"))

R_BACKEND_MAP = {
	'aws-sns': doAWSSNS
}

E_BACKEND_MAP = {
	'aws': disableAWSEvent
}

def disableEvents ():
	global conf

	for e in conf.get("disable-events", []):
		E_BACKEND_MAP[e["type"]](e)

def notifyResult (doc):
	global conf

	dumpToStream(doc, sys.stdout)

	for r in conf.get("recipients", []):
		dumpToStream(r, sys.stderr)
		R_BACKEND_MAP[r["type"]](r, doc)

def procResult (doc) -> bool:
	if not doc.get("isValid", True):
		sys.stderr.write('''* Invalid query result received.''' + os.linesep)
		return

	root = copy.copy(doc["person"])
	del root["filterOptions"]
	del root["pager"]

	if True: # DEBUG
		dumpToStream(root, sys.stderr)

	hits = root.get("hits", [])
	if len(hits) > 0:
		notifyResult(root)
		disableEvents()
		return root

def doQuery () -> bool:
	with open("query.jsonc") as q:
		json = pyjson5.load(q)
		with requests.post(
				"https://www.ratsit.se/api/search/person",
				json = json) as r:
			r.raise_for_status()
			doc = pyjson5.loads(r.text, encoding = r.encoding)
	return procResult(doc)


conf = loadConf()
if not conf.get("recipients"):
	sys.stderr.write('''* No recipient configured''' + os.linesep)
