# Name: Alex Almanza
# Date: 04/11/24
# Class: CS424-01
# Description: The following program is a search engine for a Pokémon data store,
# described in an imported .json file. This file will be specified by user at runtime.

import json
import re
from enum import Enum


# Attack data structure
class Attack:
    def __init__(self, a_name, a_description, a_damage, a_energy: dict):
        self.a_name = a_name
        self.a_description = a_description
        self.a_damage = a_damage
        self.a_energy = a_energy


# Ability data structure
class Ability:
    def __init__(self, name, description):
        self.name = name
        self.description = description


# Pokemon data structure
class Pokemon:
    def __init__(self, p_name, p_hp, p_type, p_stage, p_evolves_from, p_attacks: list, p_ability: Ability,
                 p_retreat_cost):
        self.p_name = p_name
        self.p_hp = p_hp
        self.p_type = p_type
        self.p_stage = p_stage
        self.p_evolves_from = p_evolves_from
        self.p_attacks = p_attacks
        self.p_ability = p_ability
        self.p_retreat_cost = p_retreat_cost


# Enum for search criteria, also used to get what criteria from string
class SearchCriteria(Enum):
    TYPE = 'Type'
    ATTACK_DAMAGE = 'Damage'
    HP = 'HP'
    ABILITY = 'Ability'
    STAGE = 'Stage'
    ENERGY = 'Energy'

    def from_string(self, criteria):
        if criteria.upper() == self.TYPE.value.upper():
            return self.TYPE
        if criteria.upper() == self.ATTACK_DAMAGE.value.upper():
            return self.ATTACK_DAMAGE
        if criteria.upper() == self.HP.value.upper():
            return self.HP
        if criteria.upper() == self.ABILITY.value.upper():
            return self.ABILITY
        if criteria.upper() == self.STAGE.value.upper():
            return self.STAGE
        if criteria.upper() == self.ENERGY.value.upper():
            return self.ENERGY


def get_file_data(fname):
    with open(fname) as f:
        return f.read()


# Parse the JSON dict to a dict of Pokemon() objects
def get_pokemon_dict(file_data):
    pokemon_dict = dict()

    all_pokemon = json.loads(file_data)

    for pokemon in all_pokemon:
        pokemon_data = (all_pokemon[pokemon.__str__()])

        pokemon_attacks = list()

        for attack in pokemon_data['Attacks']:

            pokemon_attack = Attack(
                a_name=attack['Name'],
                a_description=attack['Description'],
                a_damage=attack['Damage'],
                a_energy=dict()
            )

            for energy in attack['Energy']:
                pokemon_attack.a_energy[energy] = attack['Energy'][energy]

            pokemon_attacks.append(pokemon_attack)

        if pokemon_data['Ability'] is not None:
            pokemon_ability = Ability(
                name=pokemon_data['Ability']['Name'],
                description=pokemon_data['Ability']['Description']
            )
        else:
            pokemon_ability = None

        pokemon_dict[pokemon] = Pokemon(
            p_name=pokemon_data['Name'],
            p_hp=pokemon_data['HP'],
            p_type=pokemon_data['Type'],
            p_stage=pokemon_data['Stage'],
            p_evolves_from=pokemon_data['EvolvesFrom'],
            p_attacks=pokemon_attacks,
            p_ability=pokemon_ability,
            p_retreat_cost=pokemon_data['RetreatCost'],
        )

    return pokemon_dict


# String formatting of a list of Pokemon() objects
def print_pokemon_list(pokemon_list):
    if len(pokemon_list) == 0:
        print('No Pokemon found!')
        return

    print(f'\n# of Pokemon Found: {len(pokemon_list)}')
    for pokemon in pokemon_list:
        print('*' * 25 + '\n')
        print(f'{pokemon.p_name} {pokemon.p_hp}HP ({pokemon.p_type})\n{pokemon.p_stage}{(" - Evolves from " + pokemon.p_evolves_from) if pokemon.p_evolves_from is not None else ""}\nAttacks:')
        for attack in pokemon.p_attacks:
            print(f'\t{attack.a_name} - {attack.a_damage} DMG (', end='')
            for i, energy in enumerate(attack.a_energy):
                print(f'{energy}-{attack.a_energy[energy]}{", " if 0 <= i < len(attack.a_energy)-1 else ")"}', end='')
            print("\n" + attack.a_description + "\n", end='') if attack.a_description != "" else print("")
        print(f'Ability: {pokemon.p_ability.name} - {pokemon.p_ability.description}') if pokemon.p_ability is not None else print("")
        print(f'Retreat Cost - {pokemon.p_retreat_cost}\n')


# Class to make a query for Pokemon
class PokemonQuery:
    def __init__(self, criteria: SearchCriteria, args, search_dict):
        self.search_dict = search_dict
        self.criteria = criteria
        self.args = args
        self.result = []

        # All methods modify the self.result list
        if criteria == SearchCriteria.TYPE:
            self.get_pokemon_by_type()
        elif criteria == SearchCriteria.ATTACK_DAMAGE:
            self.get_pokemon_by_damage()
        elif criteria == SearchCriteria.HP:
            self.get_pokemon_by_hp()
        elif criteria == SearchCriteria.ABILITY:
            self.get_pokemon_by_ability()
        elif criteria == SearchCriteria.STAGE:
            self.get_pokemon_by_stage()
        elif criteria == SearchCriteria.ENERGY:
            self.get_pokemon_by_energy()

        # After self.result is modified, we print the result list using print_pokemon_list()
        print_pokemon_list(self.result)

    def get_pokemon_by_type(self):
        for p_name, p_data in self.search_dict.items():
            if p_data.p_type.upper() == self.args.upper():
                self.result.append(p_data)

    def get_pokemon_by_damage(self):
        for p_name, p_data in self.search_dict.items():
            for attack in p_data.p_attacks:
                # Parse the attack damage from an attack, since some of them have +,*, or -
                dmg_num = re.findall(r'\d+', attack.a_damage)
                # If an attack doesn't have damage, go to next
                if len(dmg_num) == 0: continue
                if int(dmg_num[0]) >= int(self.args):
                    self.result.append(p_data)

    def get_pokemon_by_hp(self):
        for p_name, p_data in self.search_dict.items():
            if int(p_data.p_hp) == int(self.args):
                self.result.append(p_data)

    def get_pokemon_by_ability(self):
        for p_name, p_data in self.search_dict.items():
            # Check what Pokemon have no ability if "none" specified
            if self.args.upper() == "NONE":
                if p_data.p_ability is None:
                    self.result. append(p_data)
            else:
                # If Pokemon has ability and it matches arguments, add to result list
                if p_data.p_ability is not None and p_data.p_ability.name.upper() == self.args.upper():
                    self.result.append(p_data)

    def get_pokemon_by_stage(self):
        for p_name, p_data in self.search_dict.items():
            if p_data.p_stage == "Basic":
                if self.args.upper() == "BASIC":
                    self.result.append(p_data)
            elif p_data.p_stage == "Stage 1":
                if self.args == "1":
                    self.result.append(p_data)
            elif p_data.p_stage == "Stage 2":
                if self.args == "2":
                    self.result.append(p_data)

    def get_pokemon_by_energy(self):
        for p_name, p_data in self.search_dict.items():
            for attack in p_data.p_attacks:
                for energy_type, energy_cost in attack.a_energy.items():
                    # Detect if only one argument present
                    if len(self.args) == 1:
                        # If argument is number, search for energy of cost or higher
                        if self.args.isdigit():
                            if int(energy_cost) >= int(self.args):
                                self.result.append(p_data)
                        # If argument is not number, search for energy type
                        else:
                            if energy_type.upper() == self.args.upper():
                                self.result.append(p_data)
                    # Process like before, but with 2 arguments
                    else:
                        if self.args[0].isdigit() and int(energy_cost) >= int(self.args[0]):
                            self.result.append(p_data)
                        elif not self.args[0].isdigit():
                            if energy_type.upper() == self.args[0].upper():
                                self.result.append(p_data)

                        if self.args[1].isdigit() and int(energy_cost) >= int(self.args):
                            self.result.append(p_data)
                        elif not self.args[1].isdigit():
                            if energy_type.upper() == self.args[1].upper():
                                self.result.append(p_data)

# Main method
if __name__ == '__main__':
    print('Welcome to Pokemon Search Engine. Please input the name of the JSON file containing all Pokemon.')

    # Read file input
    raw_input = input('File: ')

    # Take either raw file input (file.json) or without extension (file) then convert to file.json
    filename = raw_input.removesuffix('.json')
    filename += '.json'

    # Get pokemon data as a string
    pokemon_data = get_file_data(filename)

    # Convert pokemon data to a dictionary
    pokemon_dict = get_pokemon_dict(pokemon_data)

    # Prompt loop
    while True:

        # Ask for search criteria
        print('Please select enter a search criteria and press enter:'
              '\nSearch Criteria: type, damage, hp, ability, stage, energy'
              '\n\"type\" - All pokemon of type specified. Example arguments: \"fire\"'
              '\n\"damage\" - All pokemon with attack of minimum number of damage specified. Example arguments: \"40\"'
              '\n\"hp\" - All pokemon with amount of specified HP. Example arguments: \"60\"'
              '\n\"ability\" - All pokemon that have the specified ability name or all pokemon with no ability if \"none\" specified. Example arguments: \"Shell Armor\" or \"none\"'
              '\n\"stage\" - All pokemon of specified stage. Example arguments: \"basic\" or \"1\" or \"2\"'
              '\n\"energy\" - All pokemon with attacks that required specified type and/or amount, separated by a single space. Example arguments: \"2 Colorless\" or \"2\" or \"Colorless\" or \"Colorless 2\"')

        print('\nAn example search query would be \"type fire\" to return all fire type.')

        search = input("\nPlease enter query as \"<CRITERIA> <ARGUMENT_1> (<ARGUMENT_2>)\" with spaces between arguments: ")

        # Get arguments from search query
        search = search.split()
        arguments = ""
        for arg in range(1, len(search)):
            arguments += f'{search[arg]}{" " if arg < len(search)-1 else ""}'

        # Begin Pokemon search query. This also prints the list of Pokemon found.
        query = PokemonQuery(criteria=SearchCriteria.from_string(SearchCriteria, criteria=search[0]), search_dict=pokemon_dict, args=arguments)

        # Continue search engine
        input('\nPRESS ENTER TO CONTINUE')
