from spyre import server
import pandas as pd
import urllib2
import json
import networkx
import random   
import matplotlib
from matplotlib import pyplot as plt
import os
import numpy as np
import decision_algorithm


class DecisionInterfaceSantoriniFHG(server.App):

    title = "Decision Algorithm - Santorini - Grids"

    inputs = [{     "type":'dropdown',
                    "label": 'Scenario', 
                    "options" : [ {"label": "EQ", "value":"fhg.json"}],
                    "key": 'ticker', 
                    "action_id": "update_data"}, 

                 { "type":'slider',
                "label": "In-between grids overall (cascaded)", 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'all_cascade', 
                "action_id": 'plot'},

                 { "type":'slider',
                "label": "In-between power grids and mobile grid (cascaded)", 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'pg_mg_cascade', 
                "action_id": 'plot'},

                 { "type":'slider',
                "label": "In-between power grids and water grid (cascaded)", 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'pg_wg_cascade', 
                "action_id": 'plot'}
                ,
                 { "type":'slider',
                "label": "Mobile grid (overload)", 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'mg_over', 
                "action_id": 'plot'},

                { "type":'slider',
                "label":  "Power grid (overload)", 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'pg_over', 
                "action_id": 'plot'}, 

                { "type":'slider',
                "label": "Power grid (structural)", 
                "min" : 0,"max" : 10,"value" : 0,
                "key": "pg_struct", 
                "action_id": 'plot'},

                { "type":'slider',
                "label": "Water grid (overload)", 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'wg_over', 
                "action_id": 'plot'},

                { "type":'slider',
                "label": "Water grid (structural)" , 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'wg_struct', 
                "action_id": 'plot'}

                ]

    controls = [{   "type" : "hidden",
                    "id" : "update_data"}, {   "type" : "hidden",
                    "id" : "plot"}]

    tabs = ["Data","Ranking","Classes", "Distributions", "Info"]

    outputs = [ { "type" : "table",
                    "id" : "table_id",
                    "control_id" : "update_data",
                    "tab" : "Data",
                    "on_page_load" : True }, { "type" : "html",
                    "id" : "html3",                 
                    "tab" : "Info",
                    "on_page_load" : True },{ "type" : "html",
                    "id" : "html1",
                    "control_id" : "plot", 
                    "tab" : "Ranking",
                    "on_page_load" : True }, { "type" : "html",
                    "id" : "html2",
                    "control_id" : "plot",
                    "tab" : "Classes",
                    "on_page_load" : True }, { "type" : "plot",
                    "id" : "plot1",
                    "control_id" : "plot",
                    "tab" : "Distributions",
                    "on_page_load" : True }]

    def getData(self, params): #reads the input data
        ticker = params['ticker']
        
        data_input = 'santorini/'+ticker

        df = pd.read_json(data_input)
        return df

    def getDataOutput_Ranking(self,params): #read the output data

        ticker = params['ticker']

        weights = [params['mg_over'], params['pg_over'], params['pg_struct'], params['wg_over'],
         params['wg_struct'], params['all_cascade'], params['pg_mg_cascade'], params['pg_wg_cascade']]
        
        final_ranking, ranking_distribution = decision_algorithm.decision_ranking('santorini/fhg.json',weights,['No Mitigation', 'Redundancy within grids','Reinforcement of vulnerable nodes','UPS (uninterrupted power supply)'],
    np.array([2, 2, 2, 2, 2, 2, 2,2]), np.array([10, 10, 10, 10, 10, 10, 10, 10]), np.array([500, 500, 500, 500, 500, 500, 500, 500]))
        return (final_ranking, ranking_distribution)


    def getDataOutput_Sorting(self,params): #read the output data

        ticker = params['ticker']

        weights = [params['mg_over'], params['pg_over'], params['pg_struct'], params['wg_over'],params['wg_struct'], params['all_cascade'], params['pg_mg_cascade'], params['pg_wg_cascade']]    
        final_sorting, sorting_distribution = decision_algorithm.decision_sorting('santorini/fhg.json',weights,['No Mitigation', 'Redundancy within grids','Reinforcement of vulnerable nodes','UPS (uninterrupted power supply)'],
    np.array([2, 2, 2, 2, 2, 2, 2,2]), np.array([10, 10, 10, 10, 10, 10, 10, 10]), np.array([500, 500, 500, 500, 500, 500, 500, 500]),
    np.array(([30, 25,20,34,30,20,30,20],[50,50,50,50,50,50,50,50],[1000, 20000,18000,2000,5000,5000,6000,5000])))

        return (final_sorting, sorting_distribution)


    def html2(self,params):

        ticker = params['ticker']

        final_sorting = self.getDataOutput_Sorting(params)[0] #read from getdataoutput

        class_mit_1 = final_sorting['UPS (uninterrupted power supply)']

        class_mit_2 = final_sorting['Redundancy within grids']

        class_mit_3 = final_sorting['Reinforcement of vulnerable nodes']

        class_NoMit = final_sorting['No Mitigation']

        class_assignment = """<h1> <font size = 12> Class Assignment </font> </h1> <ul> <font size = 5><li> 
        UPS (uninterrupted power supply)<i class="badge%s">%s</i> </li> 
        <li> Redundancy within grids<i class="badge%s">%s</i> </li> 
        <li> Reinforcement of vulnerable nodes<i class="badge%s">%s</i></li>
         <li> No Mitigation<i class="badge%s">%s</i> </li> </font></ul> """%(class_mit_1,class_mit_1,class_mit_2,class_mit_2,class_mit_3,class_mit_3,class_NoMit,class_NoMit)

        return class_assignment

    def html1(self,params):
        
        ticker = params['ticker']
        
        final_ranking = self.getDataOutput_Ranking(params)[0] #read from getdataoutput

        rank_mit_1 = int(final_ranking['UPS (uninterrupted power supply)'])
        
        rank_mit_2 = int(final_ranking['Redundancy within grids'])

        rank_mit_3 = int(final_ranking['Reinforcement of vulnerable nodes'])

        rank_NoMit = int(final_ranking['No Mitigation'])
    
        ranking = """<h1> <font size = 12> Ranking </font> </h1> <ul><font size = 5> 
        <li>  UPS (uninterrupted power supply)<i class="badge%s">%s</i> </li> 
        <li> Redundancy within grids<i class="badge%s">%s</i> </li> 
        <li> Reinforcement of vulnerable nodes<i class="badge%s">%s</i> </li>
         <li> No Mitigation<i class="badge%s">%s</i> </li> </font></ul> """%(rank_mit_1,rank_mit_1,rank_mit_2,rank_mit_2,rank_mit_3,rank_mit_3,rank_NoMit,rank_NoMit) 

        return ranking

    def html3(self,params):

        description = """ 
                        <br> </br>
                        <h1> Description </h1>
                        <ul>
                        <font size = 5 > <li>This is a multicriteria algorithm to provide Decision Support in the choice of mitigation strategies in a simulated cascading effects scenario</li>
                        <li> <b> Scenario </b> allows to select a simulated cascading effect scenario.
                        <li> The numerical values on the left represent <b> weights </b> to measure the importance of the criterion for the decision maker</li>
                        <li> <b> Ranking </b> provides a relative judgement of the mitigation strategies</li>
                        <li> <b> Class assignment </b> compares mitigation strategies to predefined classes</li>
                        <li> <b> Distributions </b> represents the uncertainty of the results by perturbating simulated data and generating an array of possibile similar scenarios</li>
                        </ul>
                        <br> </br>
                        <h1> Mitigation strategies </h1>
                        <ul> <font size = 5>
                        <li> <b> UPS (Uninterrumpted Power Supply): </b> UPS for critical components, e.g. water pumps. The component is then able to work several hours without electricity supply. This strategy mitigates cascading effects across grid borders. </li>
                        <li> <b> Redundacy within grids: </b> Add some redundant grid components, e.g. additional power lines for strengthen the most vulnerable grid components. </li>
                        <li> <b> Reinforcement of vulnerable nodes: </b> Structural strength is added to critical components, e.g. a power pole could be build stronger. </li>
                        <li> <b> No Mitigation: </b> do not act on grids </li>
                        </ul>
                        <br></br>
                        <h1> Criteria </h1>
                        <ul> <font size = 5>
                        <li> <b> In-between grids overall (cascaded):</b> damages propagated in-between grids overall (cascaded) </li>
                        <li> <b> In-between power grids and mobile phone grid (cascaded):</b> damages propagated in-between power grids and mobile phone grid (cascaded)</li>
                        <li> <b> In-between power grids and water grid (cascaded)</b>: damages propagated in-between power grids and water grid (cascaded)</li>
                        <li> <b> Mobile grid (overload)</b>: damaged components in mobile phone grid (overload)</li>
                        <li> <b> Power grid (overload) </b>: damaged components in power grid (overload) </li>                        
                        <li> <b> Power grid (structural):</b> damaged components in power grid (structural)</li>
                        <li> <b> Water grid (overload) </b>: damaged components in water grid (overload)</li>
                        <li> <b> Water grid (structural) </b>: damaged components in water grid (structural)</li>    
                        </ul>
                        """
        return description

    def plot1(self, params):

        ticker = params['ticker']

        ranking_distribution = self.getDataOutput_Ranking(params)[1] #read from getdataoutput

        class_distribution = self.getDataOutput_Sorting(params)[1]        

        N = 4 #number of mitigation strategies
        
        M = 3 #number of classes

        values1 = ranking_distribution['UPS (uninterrupted power supply)']

        values2 = ranking_distribution['Redundancy within grids']

        values3 = ranking_distribution['Reinforcement of vulnerable nodes']
        
        values4 = ranking_distribution['No Mitigation']

        class1 = class_distribution['UPS (uninterrupted power supply)']

        class2 = class_distribution['Redundancy within grids']

        class3 = class_distribution['Reinforcement of vulnerable nodes']

        class4 = class_distribution['No Mitigation']

        num_1 = int(values1[0])
        num_2 = int(values1[1])
        num_3 = int(values1[2])

        values1 = [1 for i in range(num_1)] + [2 for i in range(num_2)] + [3 for i in range(num_3)]

        num_1 = int(values2[0])
        num_2 = int(values2[1])
        num_3 = int(values2[2])

        values2 = [1 for i in range(num_1)] + [2 for i in range(num_2)] + [3 for i in range(num_3)] 

        num_1 = int(values3[0])
        num_2 = int(values3[1])
        num_3 = int(values3[2])

        values3 = [1 for i in range(num_1)] + [2 for i in range(num_2)] + [3 for i in range(num_3)] 

        num_1 = int(values4[0])
        num_2 = int(values4[1])
        num_3 = int(values4[2])

        values4 = [1 for i in range(num_1)] + [2 for i in range(num_2)] + [3 for i in range(num_3)]



        num_1 = int(class1[0])
        num_2 = int(class1[1])
        num_3 = int(class1[2])

        class1 = ['a' for i in range(num_1)] + ['b' for i in range(num_2)] + ['c' for i in range(num_3)]

        class1_num = [ord(i) -96 for i in class1] #turn letters to integer, 'a' -> 1, 'b' -> 2...

        num_1 = int(class2[0])
        num_2 = int(class2[1])
        num_3 = int(class2[2])

        class2 = ['a' for i in range(num_1)] + ['b' for i in range(num_2)] + ['c' for i in range(num_3)]

        class2_num = [ord(i) -96 for i in class2] #turn letters to integer, 'a' -> 1, 'b' -> 2...

        num_1 = int(class3[0])
        num_2 = int(class3[1])
        num_3 = int(class3[2])

        class3 = ['a' for i in range(num_1)] + ['b' for i in range(num_2)] + ['c' for i in range(num_3)]

        class3_num = [ord(i) -96 for i in class3] #turn letters to integer, 'a' -> 1, 'b' -> 2...

        num_1 = int(class4[0])
        num_2 = int(class4[1])
        num_3 = int(class4[2])

        class4 = ['a' for i in range(num_1)] + ['b' for i in range(num_2)] + ['c' for i in range(num_3)]

        class4_num = [ord(i) -96 for i in class4] #turn letters to integer, 'a' -> 1, 'b' -> 2...

       # These are the "Tableau 20" colors as RGB.    
        tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    
  
       # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
        for i in range(len(tableau20)):    
            r, g, b = tableau20[i]    
            tableau20[i] = (r / 255., g / 255., b / 255.)   
    
        fig = plt.figure(1,figsize=(15, 11), dpi = 1000)    
 
        ax1 = plt.subplot(241)    
        ax1.spines["top"].set_visible(False)    
        ax1.spines["bottom"].set_visible(False)    
        ax1.spines["right"].set_visible(False)    
        ax1.spines["left"].set_visible(False) 

        ax1.get_xaxis().tick_bottom()    
        ax1.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,4.5)
        plt.ylabel("Rank Frequency", fontsize=18)  
        plt.xlabel('UPS', fontsize=18)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,N+1), fontsize = 14)
        plt.hist(values1, bins = range(1,N+2), color = tableau20[0], align = 'left', rwidth=0.9)

        ax2 = plt.subplot(242)    
        ax2.spines["top"].set_visible(False)    
        ax2.spines["bottom"].set_visible(False)    
        ax2.spines["right"].set_visible(False)    
        ax2.spines["left"].set_visible(False) 

        ax2.get_xaxis().tick_bottom()    
        ax2.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,4.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel('Redundancy', fontsize=18)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,N+1), fontsize = 14)
        plt.hist(values2, bins = range(1,N+2), color = tableau20[0], align = 'left', rwidth=0.9)

        ax3 = plt.subplot(243)    
        ax3.spines["top"].set_visible(False)    
        ax3.spines["bottom"].set_visible(False)    
        ax3.spines["right"].set_visible(False)    
        ax3.spines["left"].set_visible(False) 

        ax3.get_xaxis().tick_bottom()    
        ax3.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,4.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel("Reinforcement", fontsize=18)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,N+1), fontsize = 14)
        plt.hist(values3, bins = range(1,N+2), color = tableau20[0], align = 'left', rwidth=0.9)

        ax4 = plt.subplot(244)    
        ax4.spines["top"].set_visible(False)    
        ax4.spines["bottom"].set_visible(False)    
        ax4.spines["right"].set_visible(False)    
        ax4.spines["left"].set_visible(False) 

        ax4.get_xaxis().tick_bottom()    
        ax4.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,4.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel("No Mitigation", fontsize=18)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,N+1), fontsize = 14)
        plt.hist(values4, bins = range(1,N+2), color = tableau20[0], align = 'left', rwidth=0.9)

        cx1 = plt.subplot(245)    
        cx1.spines["top"].set_visible(False)    
        cx1.spines["bottom"].set_visible(False)    
        cx1.spines["right"].set_visible(False)    
        cx1.spines["left"].set_visible(False) 

        cx1.get_xaxis().tick_bottom()    
        cx1.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel("Class Frequency", fontsize=18)  
        plt.xlabel('UPS', fontsize=18)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,M+1), ('A','B','C'),fontsize = 14)
        plt.hist(class1_num, bins = range(1,M+2), color = tableau20[15], align = 'left', rwidth=0.9)

        cx2 = plt.subplot(246)    
        cx2.spines["top"].set_visible(False)    
        cx2.spines["bottom"].set_visible(False)    
        cx2.spines["right"].set_visible(False)    
        cx2.spines["left"].set_visible(False) 

        cx2.get_xaxis().tick_bottom()    
        cx2.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel('Redundancy', fontsize=18)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)  
        plt.xticks(range(1,M+1), ('A','B','C'),fontsize = 14)
        plt.hist(class2_num, bins = range(1,M+2), color = tableau20[15], align = 'left', rwidth=0.9)

        cx3 = plt.subplot(247)    
        cx3.spines["top"].set_visible(False)    
        cx3.spines["bottom"].set_visible(False)    
        cx3.spines["right"].set_visible(False)    
        cx3.spines["left"].set_visible(False) 

        cx3.get_xaxis().tick_bottom()    
        cx3.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel("Reinforcement", fontsize=18)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,M+1), ('A','B','C'),fontsize = 14)
        plt.hist(class3_num, bins = range(1,M+2), color = tableau20[15], align = 'left', rwidth=0.9)

        cx4 = plt.subplot(248)    
        cx4.spines["top"].set_visible(False)    
        cx4.spines["bottom"].set_visible(False)    
        cx4.spines["right"].set_visible(False)    
        cx4.spines["left"].set_visible(False) 

        cx4.get_xaxis().tick_bottom()    
        cx4.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel("No Mitigation", fontsize=18)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,M+1), ('A','B','C'),fontsize = 14)
        plt.hist(class4_num, bins = range(1,M+2), color = tableau20[15], align = 'left', rwidth=0.9)

        return fig


if __name__ == '__main__':


    app = DecisionInterfaceSantoriniFHG()
    app.launch()

