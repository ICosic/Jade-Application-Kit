#!/usr/bin/env python3
try:
    from j import AK
    
except Exception as err:
    print("Ops something went wrong: " + str(err))

AK.Api.html = """

<h1>jade Application Kit rocks</h1>
<p>hey my app is great<p>

"""

AK.Api.javascript += """

alert("Testing JavaScript");  

"""
AK.main()
