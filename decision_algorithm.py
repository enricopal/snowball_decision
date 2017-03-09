import numpy as np
import random
import networkx as nx
from operator import itemgetter
import pandas as pd
import sys
import json
import optparse

###############################################################
#### CONCORDANCE, DISCORDANCE AND CREDIBILITY FUNCTIONS  ######
###############################################################



def conc_func(i,j,k): #computes the concordance given a pair of alternatives i and j and a given criterion k
    
    x = float(alternatives[i,k] - alternatives[j,k])
    q = float(indiff_thresh[k])
    p = float(pref_thresh[k])
    if (p != q): #check that the angular coeff. exists
       if (x < q):
          return 1
       elif (x < p):
          return (-x)/(p-q) + (p)/(p-q)
       elif (x >= p):
          return 0
    else: #otherwise it is a step function
        if (x <= p):
            return 1
        else:
            return 0
    

def disc_func(i,j,k): #computes the concordance given a pair of alternatives i and j and a given criterion k
    
    x = float(alternatives[i,k] - alternatives[j,k])
    v = float(vetos[k])
    p = float(pref_thresh[k])
    
    if (p!=v):#check that the angular coeff. exists
        
       if (x <= p):
          return 0
       elif (x <= v):
          return (x)/(v-p) - (p)/(v-p)
       elif (x > v):
          return 1
        
    else: #otherwise it is a step function
        if (x <= p):
            return 0
        else:
            return 1
 


#define the concordance and discordance functions

def conc_func_tri(i,j,k): #computes the concordance given a pair alternative-profile i and j and a given criterion k
    
    x = float(alternatives[i,k] - profiles[j,k])
    q = float(indiff_thresh[k])
    p = float(pref_thresh[k])
    if (p != q): #check that the angular coeff. exists
       if (x < q):
          return 1
       elif (x < p):
          return (-x)/(p-q) + (p)/(p-q)
       elif (x >= p):
          return 0
    else: #otherwise it is a step function
        if (x <= p):
            return 1
        else:
            return 0
    
def disc_func_tri(i,j,k): #computes the concordance given a pair of alternatives i and j and a given criterion k
    
    x = float(alternatives[i,k] - profiles[j,k])
    v = float(vetos[k])
    p = float(pref_thresh[k])
    
    if (p!=v):#check that the angular coeff. exists
        
       if (x <= p):
          return 0
       elif (x <= v):
          return (x)/(v-p) - (p)/(v-p)
       elif (x > v):
          return 1
        
    else: #otherwise it is a step function
        if (x <= p):
            return 0
        else:
            return 1

def concordance_tri(i,j):
    
    c = []
    
    for k in range(m): #for each criterion
        c.append(weights[k]*conc_func_tri(i,j,k))
    
    return sum(c)



#define the credibility of the outranking as a function of concordance and discordance

def credibility_tri(i,j):
    
    c = concordance_tri(i,j)
    
    fact = c
    
    for k in range(m):#for each criterion
        d = disc_func_tri(i,j,k) #just for simplicity of notation
        if (d > c): #if the discordance of the criterion is greater than the overall concordance
            fact = fact * (1-d) / (1-c)
    
    return fact


#define the concordance and discordance for a pair of alternatives

def concordance(i,j):
    
    c = []
    
    for k in range(m): #for each criterion
        c.append(weights[k]*conc_func(i,j,k))
    
    return sum(c)



#define the credibility of the outranking as a function of concordance and discordance

def credibility(i,j):
    
    c = concordance(i,j)
    
    fact = c
    
    for k in range(m):#for each criterion
        d = disc_func(i,j,k) #just for simplicity of notation
        if (d > c): #if the discordance of the criterion is greater than the overall concordance
            fact = fact * (1-d) / (1-c)
    
    return fact

def discrimination_thresh(x):#non constant threshold
    
    return a - b*x



#########################################
############ ALGORITHMS #################
#########################################

#distillation algorithm

def compute_scores_2(cred_matrix,altern_list):
    
    n = len(altern_list)
    scores = {} #vector holding the score of each alternative
    keys = altern_list
    
    for i in keys: #initialize to 0 the scores
        scores[i] = 0
    #compute the max credibility
    
    l = max(cred_matrix.values())
    
    alpha = discrimination_thresh(l) #compute the discrimination threshold
    
    for i in altern_list: #for each alternative
        for j in altern_list:
            if i!=j: #excluding the diagonal elements
               if(cred_matrix[(i,j)] >= l - alpha):
                    scores[i] += 1
               if(cred_matrix[(j,i)] >= l - alpha):
                    scores[i] -= 1
                    
    return scores


#what happens when there are more than two alternatives

def runoff(cred_matrix,maxima_matrix, maxima):
    
    scores = {}    
    scores = compute_scores_2(maxima_matrix,maxima) #first step of the algorithm
    
    #check if there is a unique max
    maxima_run = []
    
    maximum = max(scores.values())

    for i in scores.keys():#create a list with the alternatives that have maximum score
        if scores[i] == maximum:
            maxima_run.append(i) 
    
    if len(maxima_run) == 1: #if there is a unique max
        ranking.append(maxima_run[0]) #select the winner of the competition
        #eliminate the winning alternative from the matrix
        for i,j in cred_matrix.keys():
                if i == maxima_run[0] or j == maxima_run[0]:
                    del cred_matrix[(i,j)]
                    
        altern_list.remove(maxima_run[0])
        distillation_2(cred_matrix)
        
    elif len(maxima_run) > 1:#otherwise put them all together with the same ranking
        ranking.append(maxima_run) 
        
        #eliminate the winning alternatives from the matrix
       
        
        if len(cred_matrix) > len(maxima_run):#se ho altre alternative di cui fare il ranking, rimuovo quelle ottenute
            
            #print cred_matrix
            for j in maxima_run:  
                altern_list.remove(j)
                for i,k in cred_matrix.keys():
                    if i == j or k == j:
                        del cred_matrix[(i,k)]
            #print cred_matrix.values(), maxima_run
            distillation_2(cred_matrix)
            
        else: #altrimenti l'algoritmo si ferma
            return ranking
  

  
#initializing the variables
def distillation_2(cred_matrix):
    
    #print cred_matrix
    
    if len(cred_matrix) == 1: #there is just one alternative left, the algorithm has to stop
        ranking.append(altern_list[0]) #add the last element
       
    if len(cred_matrix) > 1: #are there any more alternatives to rank?
        scores = {}    
        scores = compute_scores_2(cred_matrix,altern_list) #first step of the algorithm
        
        #check if there is a unique max
        maxima = []
        
        #index_maxima = []
        nonmaxima = []
        #nonmaxima_all = []
        #index_nonmaxima = []
        maxima_matrix = []
        maximum = max(scores.values())
        
        for i in scores.keys():#create a list with the alternatives that have maximum score
            if scores[i] == maximum:
                maxima.append(i) 
              
            else:
                nonmaxima.append(i)
 
        
        if len(maxima) == 1: #if there is a unique max
            ranking.append(maxima[0]) #select the winner of the competition
            #eliminate the winning alternative from the matrix
            
            for i,j in cred_matrix.keys():
                if i == maxima[0] or j == maxima[0]:
                    del cred_matrix[(i,j)]
                
            altern_list.remove(maxima[0])
        
            distillation_2(cred_matrix)
           
       
        if len(maxima) > 1:
            #devo costruire la sottomatrice dei massimi
            #rimuovo quelli che non sono massimi dalla matrice di credibilit
            maxima_matrix = {}
            for i in cred_matrix.keys():
                maxima_matrix[i] = cred_matrix[i]
            
            for k in nonmaxima: #elimino tutti i non_massimi
                for i,j in maxima_matrix.keys():
                    if i == k or j == k:
                        del maxima_matrix[(i,j)]
            #print cred_matrix 
            #then I apply the runoff to the submatrix of maxima
            runoff(cred_matrix,maxima_matrix, maxima)
 
    return ranking           


#what happens when there are more than two alternatives

def runoff_asc(cred_matrix,minima_matrix, minima):
    
    scores = {}    
    scores = compute_scores_2(minima_matrix,minima) #first step of the algorithm
    
    #find the minima
    minima_run = []
    
    minimum = min(scores.values())
    
    for i in scores.keys():#create a list with the alternatives that have minimum score
        if scores[i] == minimum:
            minima_run.append(i) 
    
    #check if there is a unique min
    
    if len(minima_run) == 1: #if there is a unique max
        ranking.append(minima_run[0]) #select the winner of the competition
        #eliminate the winning alternative from the matrix
        for i,j in cred_matrix.keys():
                if i == minima_run[0] or j == minima_run[0]:
                    del cred_matrix[(i,j)]
        altern_list.remove(minima_run[0])
        distillation_2_asc(cred_matrix)
        
    elif len(minima_run) > 1:#otherwise put them all together with the same ranking
        ranking.append(minima_run) 
        
        #eliminate the winning alternatives from the matrix

        if len(cred_matrix) > len(minima_run):#se ho altre alternative di cui fare il ranking, rimuovo quelle ottenute
          
           for j in minima_run:  
                altern_list.remove(j)
                for i,k in cred_matrix.keys():
                    if i == j or k == j:
                        del cred_matrix[(i,k)]
    
                      
           distillation_2_asc(cred_matrix)
            
        else: #altrimenti l'algoritmo si ferma
            
            return ranking


def distillation_2_asc(cred_matrix):
    
    #there is just one alternative left, the algorithm has to stop
    if len(cred_matrix) == 1:
        #print cred_matrix
        ranking.append(altern_list[0]) #add the last element
       
    #are there any more alternatives to rank?    
    if len(cred_matrix) > 1: 
        scores = {}    
        scores = compute_scores_2(cred_matrix,altern_list) #first step of the algorithm
        
        #find the minima
        minima = []
        
        nonminima = []
        
        minima_matrix = []
        minimum = min(scores.values())
        
        for i in scores.keys():#create a list with the alternatives that have minimum score
            if scores[i] == minimum:
                minima.append(i) 
            else:
                nonminima.append(i)
        
        if len(minima) == 1: #if there is a unique max
            ranking.append(minima[0]) #select the winner of the competition
           
            #eliminate the winning alternative from the matrix
            for i,j in cred_matrix.keys():
                if i == minima[0] or j == minima[0]:
                    del cred_matrix[(i,j)]
                    
            altern_list.remove(minima[0])
            distillation_2_asc(cred_matrix)
           
        #if there's more than a minimum
        
        if len(minima) > 1:
            #devo costruire la sottomatrice dei minimi
            #rimuovo quelli che non sono minimi dalla matrice di credibilit
            minima_matrix = {}
            for i in cred_matrix.keys():
                minima_matrix[i] = cred_matrix[i]
                
            for k in nonminima: #elimino tutti i non minimi
                for i,j in minima_matrix.keys():
                    if i == k or j == k:
                        del minima_matrix[(i,j)]
            
            #then I apply the runoff to the submatrix of maxima
            runoff_asc(cred_matrix,minima_matrix, minima)
 
    return ranking          


def ELECTREIII(x):
    
    global alternatives
    alternatives = x
    
    #################################
    ### credibility matrix ##########
    #################################
    
    cred_matrix = {} #described by a dictionary taking a tuple (i,j) as key
    
    for i in range(n): #assigning the values to the cred_matrix
       for j in range(n):
        cred_matrix[(i,j)] = credibility(i,j)
    
    ################################
    ## computing the threshold #####
    ################################
    
    #compute the max element l of the cred_matrix
    l = max(cred_matrix.values())
    #calcolo alpha

    alpha = a - b*l
    
    #############################
    ####### distillation ########
    #############################
    
    #calculating discending ranking
    global ranking
    ranking = []
    global altern_list
    altern_list = range(n)
    
    disc_order = distillation_2(cred_matrix)
    
    #calculating ascending ranking
    
    ranking = []
    altern_list = range(n)
    #reinitializing the credibility matrix
    cred_matrix = {} #described by a dictionary taking a tuple (i,j) as key
    
    for i in range(n): #assigning the values to the cred_matrix
       for j in range(n):
        cred_matrix[(i,j)] = credibility(i,j)
    '''    
    asc_order = distillation_2_asc(cred_matrix)
    #the asc_order must be reversed
    asc_order = asc_order[::-1]
    #print disc_order, asc_order
    #turning lists into dictionaries
    rank_asc = {}
    '''
    rank_disc = {}
    '''
    for i in range(len(asc_order)):
       if type(asc_order[i]) == list:#means I can iter through it
         for j in asc_order[i]:
            rank_asc[j] = i
       else: #if it is a single number I can make directly the association
         rank_asc[asc_order[i]] = i
    '''
    for i in range(len(disc_order)):
       if type(disc_order[i]) == list:
         for j in disc_order[i]:
            rank_disc[j] = i
       else:
         rank_disc[disc_order[i]] = i
    
    #######################################
    ##### combining the rankings ##########
    #######################################
    
    adjacency = np.zeros((n,n))
    '''
    #compare all pair of alternatives
    #if i outranks j in one of the two orders and j does not outrank i in the other, i outranks j in the final order
    #otherwise, they are incomparable
    #N.B. the lower the ranking, the better
    
    for i in range(n):
       for j in range(n): 
          if i != j:
             if rank_asc[i] < rank_asc[j] and rank_disc[i] <= rank_disc[j]:
                adjacency[i,j] = 1
             if rank_disc[i] < rank_disc[j] and rank_asc[i] <= rank_asc[j]:
                adjacency[i,j] = 1
                
    #creating the outranking graph
    
    G = nx.DiGraph()

    G.add_nodes_from(range(n))

    for i in range(n):
       for j in range(n):
         if adjacency[i,j] == 1:
            G.add_edge(i,j)
            
    
    indegree = nx.in_degree_centrality(G)
    rank = {}
    for i in G.nodes():
      rank[i] = (n-1)*indegree[i]

    #print asc_order
    #rescaling to an ordinal sequence
    #let us count the number of distinct elements in the indegree
    count = 1
    for i in range(len(rank.values())-1):
       if rank.values()[i] != rank.values()[i+1]:
         count += 1
    '''
    #sorted_rank = sorted(rank.iteritems(), key=itemgetter(1)) #list representing the pair of values
    sorted_rank = sorted(rank_disc.iteritems(), key=itemgetter(1)) #list representing the pair of values
    #transformation to the data 
    sorted_rank = np.array(sorted_rank)

    for i in range(len(sorted_rank) - 1):
       if sorted_rank[i + 1][1] - sorted_rank[i][1] > 1:
          sorted_rank[i + 1][1] = sorted_rank[i][1] + 1

    final_rank = {}

    for i,j in sorted_rank:
        final_rank[i] = j

    return sorted_rank


####################################
##### RUN THE ALGORITHM ############
####################################


def decision_ranking(inputs, crit_weights, mitigation_strategies, indiff, pref, veto):

    dati = pd.read_json(inputs)

    global m
    m = len(dati) #number of criteria


    #normalizing the weights

    global weights
    weights = np.array(crit_weights)

    total_weight = sum(weights)

    if total_weight == 0:

        weights = [1./m for i in range(m)]
    else:
        weights = weights/total_weight


    #parameters of the model (vectors)
    #vetos threshold
    #concordance threshold
    #discordance threshold
    global vetos, pref_thresh, indiff_thresh,a,b
    vetos = veto
    pref_thresh = pref
    indiff_thresh = indiff

    #threshold parameters    
    a = 0.3
    b = 0.15

    length = len(dati.keys()) -1

    alternatives = np.array([dati[mitigation_strategies[i]] for i in range(length)])
    global n
    n = len(alternatives) #number of strategies

    N = 101 #number of runs

    results = [] #saving the ranking for each run

    for i in range(N): #ripeto N volte
        
        #original matrix
        alternatives = np.array([dati[mitigation_strategies[i]] for i in range(length)])


        #random sampled
        alternat = np.zeros((n,m))
        
        #alternat[i,j] is the random sampling of a poissonian distribution of average alternatives[i,j]
        for i in range(n):
            for j in range(m):
                alternat[i,j] = np.random.poisson(alternatives[i,j])
        
        results.append(ELECTREIII(alternat))

    #dictionary assigning to each alternative a list of its rankings

    ranking_montecarlo = {}
    #initializing 

    for i in range(n):
        ranking_montecarlo[i] = []
    for i in results:
        
        for j in i: #coppia alternative-rank
            k = int(j[0])
            l = int(j[1])
            ranking_montecarlo[k].append(l)


    #now we can compute the median
    final_ranking_montecarlo = {}
    for i in ranking_montecarlo.keys():
        final_ranking_montecarlo[i] = np.median(ranking_montecarlo[i])


    #compute the ranking distribution
    #occurrences tells us the frequency of ranking r for alternative i
    occurrences = np.zeros((n,n))

    for i in results:
        for j in i: #coppia alternative-rank
            k = int(j[0]) #alternative
            l = int(j[1]) #rank
            occurrences[k,l] += 1 #everytime I encounter the couple, I increment the frequency

    #assign their names to the alternatives

    named_final_ranking = {}

    for i in final_ranking_montecarlo.keys():
        named_final_ranking[dati.keys()[i+1]] = final_ranking_montecarlo[i] + 1 #assegno i nomi e faccio partire il ranking da 1


    #assign the names to the ranking distributions

    ranking_distributions = {}

    var = 1

    for i in occurrences:

       ranking_distributions[dati.keys()[var]] = i
       
       var += 1

    ####################
    ### OUTPUTS DATA ###
    ####################

    #print "The medians of the ranking distributions are\n" 
    #print named_final_ranking
    #print "\n"
    #print "The ranking distributions are: \n"
    #print ranking_distributions
    return (named_final_ranking, ranking_distributions)
            



def ELECTRETri(x):
    
    global alternatives
    alternatives = x
    
    #################################
    ###### credibility matrix #######
    #################################
    
    cred_matrix = np.zeros((n,M)) #initializing the credibility matrix
    
    for i in range(n): #assigning the values to the cred_matrix
       for j in range(M):
        cred_matrix[i,j] = credibility_tri(i,j)
    
    #################################
    ### turn the fuzzy into crisp ###
    #################################
    
    for i in range(n):
        for j in range(M):
            if cred_matrix[i,j] > lambd: #if cred is greater than a threshold 
                cred_matrix[i,j] = 1
            else:
                cred_matrix[i,j] = 0
         
    ###################################
    ########## exploration ############
    ###################################
    
    pessimistic = {}

    #per ogni alternativa calcolo quali reference profiles surclassa
    for i in range(n):
        pessimistic[i] = []
        for j in range(M):
            if cred_matrix[i,j] == 1:
                pessimistic[i].append(j)
            
    #dopodich individuo il migliore fra questi

    for i in pessimistic.keys():
        pessimistic[i] = min(pessimistic.values()[i])
    
    #trasformo il dizionario in una lista ordinata
    
    pessimistic = sorted(pessimistic.iteritems(), key = itemgetter(1))
    
    return pessimistic



def decision_sorting(inputs, crit_weights,mitigation_strategies, indiff, pref, veto, prof):

    dati = pd.read_json(inputs)

    global m
    m = len(dati) #number of criteria


    #normalizing the weights

    global weights
    weights = np.array(crit_weights)

    total_weight = sum(weights)

    if total_weight == 0:

        weights = [1./m for i in range(m)]
    else:
        weights = weights/total_weight


    #parameters of the model (vectors)
    #vetos threshold
    #concordance threshold
    #discordance threshold
    global vetos, pref_thresh, indiff_thresh,lambd
    vetos = veto
    pref_thresh = pref
    indiff_thresh = indiff

    length = len(dati.keys())-1

    alternatives = np.array([dati[mitigation_strategies[i]] for i in range(length)])

    global n
    n = len(alternatives) #number of strategies   

    lambd = 0.75 

    #alternatives = np.array((dati['Basic building retrofitting'], dati['Enhanced building retrofitting'],dati['Evacuation'],dati['No mitigation']))
    #n = len(alternatives)
    global profiles
    profiles = prof
    #profiles = np.array(([5, 5,0,2,1,3,6], [25, 3500000,2500000,7000,180000,80,200],[1000, 2000000000,180000000,2000008,15020000,3000,6000]))

    global M
    M = len(profiles) #number of classes


    N = 101 #number of runs

    results = [] #saving the ranking for each run

    for i in range(N): #ripeto N volte
        
        #original matrix
        alternatives = np.array([dati[mitigation_strategies[i]] for i in range(length)])

        #random sampled
        alternat = np.zeros((n,m))
        
        #alternat[i,j] is the random sampling of a poissonian distribution of average alternatives[i,j]
        for i in range(n):
            for j in range(m):
                alternat[i,j] = np.random.poisson(alternatives[i,j])
        
        results.append(ELECTRETri(alternat))
        
    #dictionary assigning to each alternative a list of its categoriess

    sorting_montecarlo = {}
    #initializing 

    for i in range(n):
        sorting_montecarlo[i] = []
    for i in results:
        
        for j in i: #coppia alternative-rank
            k = int(j[0])
            l = int(j[1])
            sorting_montecarlo[k].append(l)


    #now we can compute the median
    final_sorting_montecarlo = {}
    for i in sorting_montecarlo.keys():
        final_sorting_montecarlo[i] = np.median(sorting_montecarlo[i])
    

    #we can assign letters instead of numbers

    for i in final_sorting_montecarlo.keys():
        if final_sorting_montecarlo[i] == 0:
            final_sorting_montecarlo[i] = 'A'
        elif final_sorting_montecarlo[i] == 1:
            final_sorting_montecarlo[i] = 'B'
        elif final_sorting_montecarlo[i] == 2:
            final_sorting_montecarlo[i] = 'C'
           

    #building the probability distribution
    #occurrences tells us the frequency of ranking r for alternative i
    occurrences = np.zeros((n,M))

    for i in results:
        for j in i: #coppia alternative-rank
            k = int(j[0]) #alternative
            l = int(j[1]) #rank
            occurrences[k,l] += 1 #everytime I encounter the couple, I increment the frequency

    #assign their names to the alternatives

    named_final_sorting = {}

    for i in final_sorting_montecarlo.keys():
        named_final_sorting[dati.keys()[i+1]] = final_sorting_montecarlo[i] #assegno i nomi e faccio partire il ranking da 1


    #assign the names to the ranking distributions

    sorting_distributions = {}

    var = 1

    for i in occurrences:

       sorting_distributions[dati.keys()[var]] = i
       
       var += 1

    ####################
    ### OUTPUTS DATA ###
    ####################


    return (named_final_sorting, sorting_distributions)




#a = decision_sorting('santorini/scenario1_input.json',[0.2,0.1,0.3,0.0,0.2,0.1,0.1],['EVC_anteEQ1','EVC_anteEQ1_anteEQ2','No Mitigation'],

#print a[0],a[1]

b = decision_ranking('santorini/scenario1_input.json',[5,3,2,1,2,0,0],['EVC_anteEQ1','EVC_anteEQ1_anteEQ2','No Mitigation'],
	np.array([0, 50, 50, 2, 50, 2, 20]), np.array([2, 100, 100, 20, 100, 20, 200]), np.array([5, 5000, 5000, 100, 5000, 100, 2000]))
print b[0],b[1]

#final_sorting, sorting_distribution = decision_sorting('santorini/fhg.json',[0.2 for i in range(8)],['UPS (uninterrupted power supply)','Redundancy within grids','Reinforcement of vulnerable nodes','No Mitigation'],
 #   np.array([5, 5, 5, 5, 5, 5, 5,5]), np.array([50, 50, 50, 50, 50, 50, 50, 50]), np.array([500, 500, 500, 500, 500, 500, 500, 500]),
 #   np.array(([30, 25,20,34,30,20,30,20],[50,50,50,50,50,50,50,50],[1000, 20000,18000,2000,5000,5000,6000,5000])))

#print final_sorting

        
#final_ranking, ranking_distribution = decision_ranking('santorini/fhg.json',[0.2 for i in range(8)],['UPS (uninterrupted power supply)','Redundancy within grids','Reinforcement of vulnerable nodes','No Mitigation'],
#    np.array([5, 5, 5, 5, 5, 5, 5,5]), np.array([50, 50, 50, 50, 50, 50, 50, 50]), np.array([500, 500, 500, 500, 500, 500, 500, 500]))

#print final_ranking





    
