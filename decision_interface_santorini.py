from spyre import server
import pandas as pd
import urllib2
import json
import networkx
import random   
import matplotlib
from matplotlib import pyplot as plt
from py4j.java_gateway import JavaGateway
import os
import decision_algorithm
import numpy as np

class DecisionInterfaceSantorini(server.App):

    title = "Decision Algorithm Santorini"

    inputs = [{     "type":'dropdown',
                    "label": 'Scenario', 
                    "options" : [ {"label": "VR-EQ1-EQ2", "value":"scenario1_input.json"}],
                    "key": 'ticker', 
                    "action_id": "update_data"}, 

                    { "type":'slider',
                "label": 'Dead', 
                "min" : 0,"max" : 10,"value" : 4,
                "key": 'dead', 
                "action_id": 'plot'},

                 { "type":'slider',
                "label": 'Direct Cost', 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'dir_cost', 
                "action_id": 'plot'},

                    { "type":'slider',
                "label": 'EM Management Cost', 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'em_cost', 
                "action_id": 'plot'},

                { "type":'slider',
                "label": 'Homeless', 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'hom', 
                "action_id": 'plot'},

                 { "type":'slider',
                "label": 'Indirect Cost', 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'ind_cost', 
                "action_id": 'plot'},

                { "type":'slider',
                "label": 'Injured', 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'inj', 
                "action_id": 'plot'},

                 { "type":'slider',
                "label": 'Sanitary Cost', 
                "min" : 0,"max" : 10,"value" : 0,
                "key": 'san_cost', 
                "action_id": 'plot'}]

    controls = [{   "type" : "hidden",
                    "id" : "update_data"}, {   "type" : "hidden",
                    "id" : "plot"},
                    {"type" : "button",
                    "label" : "Update results",
                    "id" : "update_results"}
                    ]

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
                    "control_id" : "update_results", 
                    "tab" : "Ranking",
                    "on_page_load" : True }, { "type" : "html",
                    "id" : "html2",
                    "control_id" : "update_results",
                    "tab" : "Classes",
                    "on_page_load" : True }, { "type" : "plot",
                    "id" : "plot1",
                    "control_id" : "update_results",
                    "tab" : "Distributions",
                    "on_page_load" : True }]


    def getData(self, params): #reads the input data
        ticker = params['ticker']

        data_input = 'santorini/'+ticker

        df = pd.read_json(data_input)
        return df


    def getDataOutput_Ranking(self,params): #read the output data

        ticker = params['ticker']

        weights = [params['dead'], params['dir_cost'], params['em_cost'], params['hom'], params['ind_cost'], params['inj'], params['san_cost']]
        
        final_ranking, ranking_distribution = decision_algorithm.decision_ranking('santorini/scenario1_input.json',weights,['EVC_anteEQ1','EVC_anteEQ1_anteEQ2','No Mitigation'],
    np.array([0, 50, 50, 2, 50, 2, 20]), np.array([2, 100, 100, 20, 100, 20, 200]), np.array([5, 5000, 5000, 100, 5000, 100, 2000]))
        return (final_ranking, ranking_distribution)


    def getDataOutput_Sorting(self,params): #read the output data

        ticker = params['ticker']

        weights = [params['dead'], params['dir_cost'], params['em_cost'], params['hom'], params['ind_cost'], params['inj'], params['san_cost']]
    
        final_sorting, sorting_distribution = decision_algorithm.decision_sorting('santorini/scenario1_input.json',weights,['EVC_anteEQ1','EVC_anteEQ1_anteEQ2','No Mitigation'],
    np.array([0, 50, 50, 2, 50, 2,20]),np.array([2, 100, 100, 20, 100, 20, 200]),np.array([5, 5000, 5000, 100, 5000, 100, 2000]),
    np.array(([20, 3300000,2300000,2050,655000,60,120],
     [30, 3600000,2500000,2070,700000,100,200],
     [1000, 2000000000,180000000,2000008,15020000,3000,6000])))

        return (final_sorting, sorting_distribution)

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
                        <li> <b> EVC_anteEQ1: </b> evacuate all the population before first earthquake </li>
                        <li> <b> EVC_anteEQ1_anteEQ2: </b> evacuate tourists before EQ1 and the rest of the population after EQ2 </li>
                        <li> <b> No Mitigation: </b> do not evacuate the population </li>
                        </ul>
                        <br></br>
                        <h1> Criteria </h1>
                        <ul> <font size = 5>
                        <li> <b> Dead: </b> number of victims </li>
                        <li> <b> Direct Cost: </b> sum of direct costs </li>
                        <li> <b> EM Management Cost: </b> emergency management cost </li>
                        <li> <b> Homeless: </b> number of homeless people </li>
                        <li> <b> Indirect Cost: </b> sum of indirect costs  </li>
                        <li> <b> Injured: </b> number of injured people </li>
                        <li> <b> Sanitary Cost: </b> sum of sanitary costs </li>
                        </ul>
                        """
        return description

    def html2(self,params):

        ticker = params['ticker']

        final_sorting = self.getDataOutput_Sorting(params)[0] #read from getdataoutput

        class_EVC_t0 = final_sorting['EVC_anteEQ1_anteEQ2']

        class_EVC_t1 = final_sorting['EVC_anteEQ1']

        class_NoMit = final_sorting['No Mitigation']

        class_assignment = """<h1> <font size = 13> Class Assignment </font> </h1> <ul> <font size = 6><li> 
        Evacuation anteEQ1 anteEQ2 <i class="badge%s">%s</i> </li> <li>  Evacuation anteEQ1 <i class="badge%s">%s</i>  </li> <li> 
        No Mitigation <i class="badge%s">%s</i>  </li> </font></ul> """%(class_EVC_t0,class_EVC_t0,class_EVC_t1,class_EVC_t1,class_NoMit,class_NoMit)

        return class_assignment

    def html1(self,params):
        
        ticker = params['ticker']
        
        final_ranking = self.getDataOutput_Ranking(params)[0] #read from getdataoutput

        rank_EVCA = final_ranking['EVC_anteEQ1_anteEQ2']

        rank_EVCA = int(rank_EVCA)
        
        rank_EVCB = final_ranking['EVC_anteEQ1']

        rank_EVCB = int(rank_EVCB)

        rank_NoMit = final_ranking['No Mitigation']

        rank_NoMit = int(rank_NoMit)
    
        ranking = """<h1> <font size = 13> Ranking </font> </h1> <ul><font size = 6> <li> Evacuation anteEQ1 anteEQ2<i class="badge%s">%s</i> </li> 
        <li> Evacuation anteEQ1 <i class="badge%s">%s</i> </li> <li>
         No Mitigation <i class="badge%s">%s</i> </li> </font></ul>
          """%(rank_EVCA,rank_EVCA,rank_EVCB,rank_EVCB,rank_NoMit,rank_NoMit) 

        return ranking

    def plot1(self, params):

        ticker = params['ticker']

        ranking_distribution = self.getDataOutput_Ranking(params)[1] #read from getdataoutput
        
        #print ranking_distribution

        class_distribution = self.getDataOutput_Sorting(params)[1]

        N = 3 #number of mitigation strategies
        
        M = 3 #number of classes

        values1 = ranking_distribution['EVC_anteEQ1_anteEQ2']

        num_1 = int(values1[0])
        num_2 = int(values1[1])
        num_3 = int(values1[2])

        values1 = [1 for i in range(num_1)] + [2 for i in range(num_2)] + [3 for i in range(num_3)]

        values2 = ranking_distribution['EVC_anteEQ1']

        num_1 = int(values2[0])
        num_2 = int(values2[1])
        num_3 = int(values2[2])

        values2 = [1 for i in range(num_1)] + [2 for i in range(num_2)] + [3 for i in range(num_3)] 

        values4 = ranking_distribution['No Mitigation']

        num_1 = int(values4[0])
        num_2 = int(values4[1])
        num_3 = int(values4[2])

        values4 = [1 for i in range(num_1)] + [2 for i in range(num_2)] + [3 for i in range(num_3)]

        class1 = class_distribution['EVC_anteEQ1_anteEQ2']

        num_1 = int(class1[0])
        num_2 = int(class1[1])
        num_3 = int(class1[2])

        class1 = ['a' for i in range(num_1)] + ['b' for i in range(num_2)] + ['c' for i in range(num_3)]

        class1_num = [ord(i) -96 for i in class1] #turn letters to integer, 'a' -> 1, 'b' -> 2...

        class2 = class_distribution['EVC_anteEQ1']

        num_1 = int(class2[0])
        num_2 = int(class2[1])
        num_3 = int(class2[2])

        class2 = ['a' for i in range(num_1)] + ['b' for i in range(num_2)] + ['c' for i in range(num_3)]

        class2_num = [ord(i) -96 for i in class2] #turn letters to integer, 'a' -> 1, 'b' -> 2...

        class4 = class_distribution['No Mitigation']

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
 
        ax1 = plt.subplot(231)    
        ax1.spines["top"].set_visible(False)    
        ax1.spines["bottom"].set_visible(False)    
        ax1.spines["right"].set_visible(False)    
        ax1.spines["left"].set_visible(False) 

        ax1.get_xaxis().tick_bottom()    
        ax1.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel("Rank Frequency", fontsize=20)  
        plt.xlabel('EVC_anteEQ1_anteEQ2', fontsize=20)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,N+1), fontsize = 14)
        plt.hist(values1, bins = range(1,N+2), color = tableau20[0], align = 'left', rwidth=0.9)

        ax2 = plt.subplot(232)    
        ax2.spines["top"].set_visible(False)    
        ax2.spines["bottom"].set_visible(False)    
        ax2.spines["right"].set_visible(False)    
        ax2.spines["left"].set_visible(False) 

        ax2.get_xaxis().tick_bottom()    
        ax2.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel('EVC_anteEQ1', fontsize=20)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,N+1), fontsize = 14)
        plt.hist(values2, bins = range(1,N+2), color = tableau20[0], align = 'left', rwidth=0.9)

        ax4 = plt.subplot(233)    
        ax4.spines["top"].set_visible(False)    
        ax4.spines["bottom"].set_visible(False)    
        ax4.spines["right"].set_visible(False)    
        ax4.spines["left"].set_visible(False) 

        ax4.get_xaxis().tick_bottom()    
        ax4.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel("No Mitigation", fontsize=20)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,N+1), fontsize = 14)
        plt.hist(values4, bins = range(1,N+2), color = tableau20[0], align = 'left', rwidth=0.9)

        cx1 = plt.subplot(234)    
        cx1.spines["top"].set_visible(False)    
        cx1.spines["bottom"].set_visible(False)    
        cx1.spines["right"].set_visible(False)    
        cx1.spines["left"].set_visible(False) 

        cx1.get_xaxis().tick_bottom()    
        cx1.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel("Class Frequency", fontsize=20)  
        plt.xlabel("EVC_anteEQ1_anteEQ2", fontsize=20)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,M+1), ('A','B','C'),fontsize = 14)
        plt.hist(class1_num, bins = range(1,M+2), color = tableau20[15], align = 'left', rwidth=0.9)

        cx2 = plt.subplot(235)    
        cx2.spines["top"].set_visible(False)    
        cx2.spines["bottom"].set_visible(False)    
        cx2.spines["right"].set_visible(False)    
        cx2.spines["left"].set_visible(False) 

        cx2.get_xaxis().tick_bottom()    
        cx2.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel("EVC_anteEQ1", fontsize=20)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,M+1), ('A','B','C'),fontsize = 14)
        plt.hist(class2_num, bins = range(1,M+2), color = tableau20[15], align = 'left', rwidth=0.9)

        cx4 = plt.subplot(236)    
        cx4.spines["top"].set_visible(False)    
        cx4.spines["bottom"].set_visible(False)    
        cx4.spines["right"].set_visible(False)    
        cx4.spines["left"].set_visible(False) 

        cx4.get_xaxis().tick_bottom()    
        cx4.get_yaxis().tick_left()    
        plt.ylim(0,150)  
        plt.xlim(0.5,3.5)
        plt.ylabel(" ", fontsize=18)  
        plt.xlabel("No Mitigation", fontsize=20)  

        plt.yticks(range(0,len(class2)+1,20), fontsize=14)     
        plt.xticks(range(1,M+1), ('A','B','C'),fontsize = 14)
        plt.hist(class4_num, bins = range(1,M+2), color = tableau20[15], align = 'left', rwidth=0.9)

        return fig




if __name__ == '__main__':
    

    app = DecisionInterfaceSantorini()
    app.launch(port = 80, host = '192.168.30.22')

