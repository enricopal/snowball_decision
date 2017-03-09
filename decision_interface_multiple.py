    #!/user/bin/env python

from spyre.server import Site, App
#from py4j.java_gateway import JavaGateway

import os
from decision_interface_santorini import DecisionInterfaceSantorini
from decision_interface_santorini_fhg import DecisionInterfaceSantoriniFHG
#from decision_interface_hungary import DecisionInterfaceHungary


class Index(App):
    def getHTML(self, params):
        return "Title Page Here"

#os.system('javac -cp \* ContextModule.java') #compile the source
#os.system('gnome-terminal -e \"java -cp .:\* ContextModule\"') #run the instance on a separate shell
#os.system('java -cp .:\* ContextModule &') 

#gateway = JavaGateway() #launch the gateway server

#context_module = gateway.entry_point # get the ContextModule instance

a = DecisionInterfaceSantorini()
b = DecisionInterfaceSantoriniFHG()

#a.define_context(context_module)
#b.define_context(context_module)
#c.define_context(context_module)

site = Site(DecisionInterfaceSantorini)

site.addApp(DecisionInterfaceSantoriniFHG, '/app2')
#site.addApp(DecisionInterfaceHungary, '/app2/app3')


site.launch()






