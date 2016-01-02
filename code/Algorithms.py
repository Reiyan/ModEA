#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

__author__ = 'Sander van Rijn <svr003@gmail.com>'
# External libraries
from copy import copy
from numpy import floor, log
from numpy.random import randn
# Internal classes
from .Individual import Individual
from .Parameters import Parameters
# Internal modules
import code.Mutation as Mut
import code.Recombination as Rec
import code.Selection as Sel
import code.Sampling as Sam


# Example algorithms
def onePlusOneES(n, fitnessFunction, budget):
    """
        Implementation of the default (1+1)-ES
        Requires the length of the vector to be optimized, the handle of a fitness function to use and the budget

        :param n:               Dimensionality of the problem to be solved
        :param fitnessFunction: Function to determine the fitness of an individual
        :param budget:          Number of function evaluations allowed for this algorithm
        :returns:               The statistics generated by running the algorithm
    """

    parameters = Parameters(n, budget, 1, 1)
    population = [Individual(n)]
    population[0].fitness = fitnessFunction(population[0].dna)

    # We use functions here to 'hide' the additional passing of parameters that are algorithm specific
    def recombine(pop):
        return Rec.onePlusOne(pop)  # simply copy the only existing individual and return as a list
    def mutate(ind):
        return Mut.x1(ind, parameters, Sam.GaussianSampling(n))
    def select(pop, new_pop, t):
        return Sel.onePlusOneSelection(pop, new_pop, t, parameters)
    def mutateParameters(t, _):
        return parameters.oneFifthRule(t)

    functions = {
        'recombine': recombine,
        'mutate': mutate,
        'select': select,
        'mutateParameters': mutateParameters,
    }

    return baseAlgorithm(population, fitnessFunction, budget, functions, parameters)


def CMA_ES(n, fitnessFunction, budget, mu=None, lambda_=None, elitist=False):
    """
        Implementation of a default (mu +/, lambda)-CMA-ES
        Requires the length of the vector to be optimized, the handle of a fitness function to use and the budget

        :param n:               Dimensionality of the problem to be solved
        :param fitnessFunction: Function to determine the fitness of an individual
        :param budget:          Number of function evaluations allowed for this algorithm
        :param mu:              Number of individuals that form the parents of each generation
        :param lambda_:         Number of individuals in the offspring of each generation
        :param elitist:         Boolean switch on using a (mu, l) strategy rather than (mu + l). Default: False
        :returns:               The statistics generated by running the algorithm
    """

    parameters = Parameters(n, budget, mu, lambda_, elitist=elitist)
    population = [Individual(n) for _ in range(mu)]

    # Artificial init: in hopes of fixing CMA-ES
    wcm = parameters.wcm
    fitness = fitnessFunction(wcm)[0]
    for individual in population:
        individual.dna = wcm
        individual.fitness = fitness

    # We use functions here to 'hide' the additional passing of parameters that are algorithm specific
    def recombine(pop):
        return Rec.weighted(pop, parameters)
    def mutate(ind):
        return Mut.CMAMutation(ind, parameters, Sam.GaussianSampling(n))
    def select(pop, new_pop, t):
        return Sel.best(pop, new_pop, parameters)
    def mutateParameters(t, _):
        return parameters.adaptCovarianceMatrix(t, None)

    functions = {
        'recombine': recombine,
        'mutate': mutate,
        'select': select,
        'mutateParameters': mutateParameters,
    }

    return baseAlgorithm(population, fitnessFunction, budget, functions, parameters)


def onePlusOneCholeskyCMAES(n, fitnessFunction, budget):
    """
        Implementation of the default (1+1)-ES
        Requires the length of the vector to be optimized, the handle of a fitness function to use and the budget

        :param n:               Dimensionality of the problem to be solved
        :param fitnessFunction: Function to determine the fitness of an individual
        :param budget:          Number of function evaluations allowed for this algorithm
        :returns:               The statistics generated by running the algorithm
    """

    parameters = Parameters(n, budget, 1, 1)
    population = [Individual(n)]
    population[0].fitness = fitnessFunction(population[0].dna)

    # We use functions here to 'hide' the additional passing of parameters that are algorithm specific
    def recombine(pop):
        return Rec.onePlusOne(pop)  # simply copy the only existing individual and return as a list
    def mutate(ind):
        return Mut.choleskyCMAMutation(ind, parameters, Sam.GaussianSampling(n))
    def select(pop, new_pop, t):
        return Sel.onePlusOneCholeskySelection(pop, new_pop, parameters)
    def mutateParameters(t, _):
        return parameters.adaptCholeskyCovarianceMatrix()

    functions = {
        'recombine': recombine,
        'mutate': mutate,
        'select': select,
        'mutateParameters': mutateParameters,
    }

    return baseAlgorithm(population, fitnessFunction, budget, functions, parameters)


def onePlusOneActiveCMAES(n, fitnessFunction, budget):
    """
        Implementation of the default (1+1)-ES
        Requires the length of the vector to be optimized, the handle of a fitness function to use and the budget

        :param n:               Dimensionality of the problem to be solved
        :param fitnessFunction: Function to determine the fitness of an individual
        :param budget:          Number of function evaluations allowed for this algorithm
        :returns:               The statistics generated by running the algorithm
    """

    parameters = Parameters(n, budget, 1, 1)
    population = [Individual(n)]
    population[0].fitness = fitnessFunction(population[0].dna)
    parameters.addToFitnessHistory(population[0].fitness)

    # We use functions here to 'hide' the additional passing of parameters that are algorithm specific
    def recombine(pop):
        return Rec.onePlusOne(pop)  # simply copy the only existing individual and return as a list
    def mutate(ind):
        return Mut.choleskyCMAMutation(ind, parameters, Sam.GaussianSampling(n))
    def select(pop, new_pop, _):
        return Sel.onePlusOneActiveSelection(pop, new_pop, parameters)
    def mutateParameters(t, _):
        return parameters.adaptActiveCovarianceMatrix()

    functions = {
        'recombine': recombine,
        'mutate': mutate,
        'select': select,
        'mutateParameters': mutateParameters,
    }

    return baseAlgorithm(population, fitnessFunction, budget, functions, parameters)


def CMSA_ES(n, fitnessFunction, budget, mu=None, lambda_=None, elitist=False):
    """
        Implementation of a default (mu +/, lambda)-CMA-ES
        Requires the length of the vector to be optimized, the handle of a fitness function to use and the budget

        :param n:               Dimensionality of the problem to be solved
        :param fitnessFunction: Function to determine the fitness of an individual
        :param budget:          Number of function evaluations allowed for this algorithm
        :param mu:              Number of individuals that form the parents of each generation
        :param lambda_:         Number of individuals in the offspring of each generation
        :param elitist:         Boolean switch on using a (mu, l) strategy rather than (mu + l). Default: False
        :returns:               The statistics generated by running the algorithm
    """

    parameters = Parameters(n, budget, mu, lambda_, elitist=elitist, weights_option='1/n')
    population = [Individual(n) for _ in range(mu)]
    for individual in population:
        individual.fitness = fitnessFunction(individual.dna)

    # We use functions here to 'hide' the additional passing of parameters that are algorithm specific
    def recombine(pop):
        return Rec.weighted(pop, parameters)
    def mutate(ind):
        return Mut.CMAMutation(ind, parameters, Sam.GaussianSampling(n))
    def select(pop, new_pop, _):
        return Sel.best(pop, new_pop, parameters)
    def mutateParameters(t, _):
        return parameters.selfAdaptCovarianceMatrix()

    functions = {
        'recombine': recombine,
        'mutate': mutate,
        'select': select,
        'mutateParameters': mutateParameters,
    }

    return baseAlgorithm(population, fitnessFunction, budget, functions, parameters)


# Evolving ES
def customizedES(n, fitnessFunction, budget, mu=None, lambda_=None, opts=None):
    """
        This function accepts a dictionary of options 'opts' which selects from a large range of different
        functions and combinations of those. Instrumental in Evolving Evolution Strategies

        :param n:               Dimensionality of the problem to be solved
        :param fitnessFunction: Function to determine the fitness of an individual
        :param budget:          Number of function evaluations allowed for this algorithm
        :param mu:              Number of individuals that form the parents of each generation
        :param lambda_:         Number of individuals in the offspring of each generation
        :param opts:            Dictionary containing the options (elitist, active, threshold, etc) to be used
        :returns:               The statistics generated by running the algorithm
    """

    if lambda_ is None:
        lambda_ = int(4 + floor(3 * log(n)))
    if mu is None:
        mu = int(lambda_//2)

    # Boolean defaults, if not given
    bool_default_opts = ['active', 'elitism', 'mirrored', 'orthogonal', 'sequential', 'threshold', 'two-point']
    for op in bool_default_opts:
        if op not in opts:
            opts[op] = False

    # String defaults, if not given
    string_default_opts = ['base-sampler', 'ipop', 'selection', 'weights']
    for op in string_default_opts:
        if op not in opts:
            opts[op] = None


    # Pick the lowest-level sampler
    if opts['base-sampler'] == 'quasi-sobol':
        sampler = Sam.QuasiGaussianSobolSampling(n)
    elif opts['base-sampler'] == 'quasi-halton' and Sam.halton_available:
        sampler = Sam.QuasiGaussianHaltonSampling(n)
    else:
        sampler = Sam.GaussianSampling(n)

    # Create an orthogonal sampler using the determined base_sampler
    if opts['orthogonal']:
        sampler = Sam.OrthogonalSampling(n, base_sampler=sampler)

    # Create a mirrored sampler using the sampler (structure) chosen so far
    if opts['mirrored']:
        sampler = Sam.MirroredSampling(n, base_sampler=sampler)

    if opts['selection'] == 'pairwise':
        selector = Sel.pairwise
        # TODO FIXME: are these fixes correct?!
        # Explicitly force lambda_ to be even
        if lambda_ % 2 == 1:
            lambda_ += 1

        # Both pairwise selection and TPA are lambda-reducing procedures. Change mu if naively using default settings
        if opts['two-point']:
            eff_lambda = lambda_ - 2
        else:
            eff_lambda = lambda_

        if mu > eff_lambda // 2:
            mu = eff_lambda // 2
    else:
        selector = Sel.best


    parameters = Parameters(n, budget, mu, lambda_, weights_option=opts['weights'], active=opts['active'],
                            elitist=opts['elitism'], ipop=opts['ipop'], sequential=opts['sequential'],
                            tpa=opts['two-point'])
    if opts['sequential'] and opts['selection'] == 'pairwise':
        parameters.seq_cutoff = 2*mu
    population = [Individual(n) for _ in range(parameters.mu)]

    # Artificial init: in hopes of fixing CMA-ES
    wcm = parameters.wcm
    fitness = fitnessFunction(wcm)[0]
    for individual in population:
        individual.dna = wcm
        individual.fitness = fitness

    # We use functions here to 'hide' the additional passing of parameters that are algorithm specific
    def recombine(pop):
        return Rec.weighted(pop, parameters)
    def mutate(ind):
        return Mut.CMAMutation(ind, parameters, sampler, threshold_convergence=opts['threshold'])
    def select(pop, new_pop, _):
        return selector(pop, new_pop, parameters)
    def mutateParameters(t, tpa):
        return parameters.adaptCovarianceMatrix(t, tpa)

    functions = {
        'recombine': recombine,
        'mutate': mutate,
        'select': select,
        'mutateParameters': mutateParameters,
    }

    return baseAlgorithm(population, fitnessFunction, budget, functions, parameters)



def baseAlgorithm(population, fitnessFunction, budget, functions, parameters):
    """
        Skeleton function for all ES algorithms
        Requires a population, fitness function handle, evaluation budget and the algorithm-specific functions

        The algorithm-specific functions should (roughly) behave as follows:

         - recombine:           The current population (mu individuals) is passed to this function,
                                and should return a new population (lambda individuals),
                                generated by some form of recombination

         - mutate:              An individual is passed to this function and should be mutated 'in-line',
                                no return is expected

         - select:              The original parents, new offspring and used budget are passed to this function,
                                and should return a new population (mu individuals) after
                                (mu+lambda) or (mu,lambda) selection

         - mutateParameters:    Mutates and/or updates all parameters where required


        :param population:      Initial set of individuals that form the starting population of the algorithm
        :param fitnessFunction: Function to determine the fitness of an individual
        :param budget:          Number of function evaluations allowed for this algorithm
        :param functions:       Dict with (lambda) functions 'recombine', 'mutate', 'select' and 'mutateParameters'
        :param parameters:      Parameters object for storing relevant settings
        :returns:               The statistics generated by running the algorithm
    """

    # Parameter tracking
    sigma_over_time = [parameters.sigma_mean]
    best_fitness_over_time = [population[0].fitness]
    best_individual = population[0]

    improvement_found = False  # Has a better individual has been found? Used for sequential evaluation
    tpa_result = None          # Is the ideal step size larger (True) or smaller (False)? None if TPA is not used

    # Initialization
    used_budget = 0
    used_budget_at_last_restart = 0
    restart_budget = parameters.max_iter
    recombine = functions['recombine']
    mutate = functions['mutate']
    select = functions['select']
    mutateParameters = functions['mutateParameters']
    sequential_evaluation = parameters.sequential
    two_point_adaptation = parameters.tpa

    # Single recombination outside the eval loop to create the new population
    new_population = recombine(population)

    # The main evaluation loop
    while used_budget < budget:

        if two_point_adaptation:
            new_population = new_population[:-2]

        for i, individual in enumerate(new_population):
            mutate(individual)  # Mutation
            # Evaluation
            individual.fitness = fitnessFunction(individual.dna)[0]  # fitnessFunction returns as a list, as it allows
            used_budget += 1                                         # simultaneous evaluation for multiple individuals

            # Sequential Evaluation
            if sequential_evaluation:  # Sequential evaluation: we interrupt once a better individual has been found
                if individual.fitness < best_individual.fitness:
                    improvement_found = True  # Is the latest individual better?
                if i >= parameters.seq_cutoff and improvement_found:
                    improvement_found = False  # Have we evaluated at least mu mutated individuals?
                    break
                if used_budget == budget:
                    break

        new_population = new_population[:i+1]  # Any un-used individuals in the new population are discarded
        fitnesses = sorted([individual.fitness for individual in new_population])
        population = select(population, new_population, used_budget)  # Selection

        # Track parameters
        sigma_over_time.extend([parameters.sigma_mean] * (used_budget - len(sigma_over_time)))
        best_fitness_over_time.extend([population[0].fitness] * (used_budget - len(best_fitness_over_time)))
        if population[0].fitness < best_individual.fitness:
            best_individual = copy(population[0])

        # We can stop here if we know we reached our budget
        if used_budget >= budget:
            break

        if len(population) == parameters.mu:
            new_population = recombine(population)                        # Recombination
        else:
            print('Bad population size! size: {} instead of {} at used budget {}'.format(len(population),
                                                                                         parameters.mu, used_budget))

        # Two-Point step-size Adaptation
        # TODO: Move the following code to >= 1 separate function(s)
        if two_point_adaptation:
            wcm = parameters.wcm
            tpa_vector = (wcm - parameters.wcm_old) * parameters.tpa_factor

            tpa_fitness_plus = fitnessFunction(wcm + tpa_vector)[0]
            tpa_fitness_min = fitnessFunction(wcm - tpa_vector)[0]

            used_budget += 2
            if used_budget > budget and sequential_evaluation:
                used_budget = budget

            if tpa_fitness_plus < tpa_fitness_min:
                tpa_result = 1
            else:
                tpa_result = -1

        mutateParameters(used_budget, tpa_result)                     # Parameter mutation

        # (B)IPOP
        # TODO: Move the following code to >= 1 separate function(s)
        if parameters.ipop:
            used_budget_since_restart = used_budget - used_budget_at_last_restart
            restart = True if used_budget_since_restart > restart_budget else False
            if not restart:
                restart = parameters.ipopTest(used_budget, fitnesses)

            if restart:
                used_budget_at_last_restart = used_budget
                # Most restrictive restart scheme
                if parameters.ipop == 'BIPOP' and parameters.last_pop == 'large'\
                                              and used_budget_since_restart//2 < budget-used_budget:
                    restart_budget = used_budget_since_restart//2
                    pop_change = 'small'
                # In the remaining (B)IPOP cases we increase the population
                elif parameters.ipop in ['IPOP', 'BIPOP']:
                    restart_budget = parameters.max_iter * parameters.lambda_  # TODO FIXME: add * parameters.lambda_ factor?!
                    pop_change = 'large'
                # Otherwise, we just use a local restart TODO FIXME: DOES NOT CURRENTLY OCCUR?
                else:
                    pop_change = None

                print("restart! {}".format(pop_change))
                parameters.local_restart(pop_change=pop_change)
                # Set population to start from a new random search point
                new_search_point = randn(parameters.n,1)
                for ind in new_population:
                    ind.dna = new_search_point

    # Debug print statement, displaying the number of degenerations that occurred during the run of this algorithm
    if parameters.count_degenerations:
        print(parameters.count_degenerations, end=' ')

    return population, sigma_over_time, best_fitness_over_time, best_individual
