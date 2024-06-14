import time
import ratsitlarm


while not ratsitlarm.doQuery():
	time.sleep(float(1800))
