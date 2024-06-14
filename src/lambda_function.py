import ratsitlarm


def lambda_handler (event, context):
	return ratsitlarm.doQuery()
