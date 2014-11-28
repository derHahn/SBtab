#!/usr/bin/env python
import libsbml, numpy, tablibIO, SBtab

allowed_sbtabs = ['Reaction','Compound','Compartment','Quantity']

class ConversionError(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return self.message

class SBMLDocument:
    '''
    SBML model to be converted to SBtab file/s
    '''
    def __init__(self,sbml_file,filename):
        '''
        initalize SBtab document, check it for SBtabs
        '''
        try: self.model = sbml_file.getModel()
        except: print 'The model that you have entered is not a valid SBML file. Please see the readme.txt to see how this is done properly.'
        self.filename = filename
        if not self.filename.endswith('.xml'): 
            raise ConversionError('The given file format is not supported: '+self.filename)

        #for testing purposes:
        #sbtabs = self.makeSBtabs()
        #for sbtab in sbtabs:
        #    print sbtab
        #    print '\n\n\n'
        
    def makeSBtabs(self):
        '''
        generates the SBtab files
        '''
        sbtabs = []

        for sbtab_type in allowed_sbtabs:
            function_name = 'self.'+sbtab_type.lower()+'SBtab()'
            try: sbtabs.append(eval(function_name))
            except: print 'There were troubles generating the',sbtab_type,'SBtab for',self.filename,'. Please see the readme.txt to see how this is done properly.'
        sbtabs = self.getRidOfNone(sbtabs)

        sbtab_objects = []
        for sbtab in sbtabs:
            new_tablib_obj = tablibIO.importSetNew(sbtab[0],'sbtab.tsv')
            single_tab     = SBtab.SBtabTable(new_tablib_obj,'sbtab.tsv')
            sbtab_objects.append(single_tab)

        return sbtab_objects
        
    def getRidOfNone(self,sbtabs):
        '''
        remove empty SBtabs (if no values for an SBtab were provided by the SBML)
        '''
        new_tabs = []
        for element in sbtabs:
            if element != None:
                new_tabs.append(element)
        return new_tabs

    def compartmentSBtab(self):
        '''
        build a Compartment SBtab
        '''
        compartment_SBtab = '!!SBtab SBtabVersion="0.8" Document="'+self.filename.rstrip('.xml')+'" TableType="Compartment" TableName="Compartment"\n!Compartment\t!Name\t!Size\t!Unit\t!SBOTerm\n'

        for compartment in self.model.getListOfCompartments():
            value_row = compartment.getId()+'\t'
            try: value_row += str(compartment.getName())+'\t'
            except: value_row += '\t'
            try: value_row += str(compartment.getSize())+'\t'
            except: value_row += '\t'
            try: value_row += str(compartment.getUnits())+'\t'
            except: value_row += '\t'           
            if str(compartment.getSBOTerm()) == '-1': value_row += '\n'
            else: str(compartment.getSBOTerm())+'\n'            
            #try: value_row += str(compartment.getSBOTerm())+'\n'
            #except: value_row += '\t\n'
            compartment_SBtab += value_row

        return [compartment_SBtab,'compartment']
        
    def compoundSBtab(self):
        '''
        builds a Compound SBtab
        '''
        compound_SBtab = '!!SBtab SBtabVersion="0.8" Document="'+self.filename.rstrip('.xml')+'" TableType="Compound" TableName="Compound"\n!Compound\t!Name\t!Location\t!Charge\t!IsConstant\t!SBOTerm\t!InitialConcentration\n'

        for species in self.model.getListOfSpecies():
            value_row = species.getId()+'\t'
            value_row += species.getName()+'\t'
            try: value_row += species.getCompartment()+'\t'
            except: value_row += '\t'
            try: value_row += str(species.getCharge())+'\t'
            except: value_row += '\t'
            try: value_row += str(species.getConstant())+'\t'
            except: value_row += '\t'
            if str(species.getSBOTerm()) == '-1': value_row += '\t'
            else: str(species.getSBOTerm())+'\t'
            #try: value_row += str(species.getSBOTerm())+'\t'
            #except: value_row += '\t'
            try: value_row += str(species.getInitialConcentration())+'\n'
            except: value_row += '\t\n'
            '''
            dsds = species.getCVTerms()
            for i in range(species.getNumCVTerms()):
                cvterm = dsds.get(i)
                print cvterm.getResourceURI(i)
            try: value_row += species.getAnnotation()+'\n'
            except: value_row += '\t\n'
            '''
            compound_SBtab += value_row
            
        return [compound_SBtab,'compound']


    def reactionSBtab(self):
        '''
        builds a Reaction SBtab
        '''
        reaction_SBtab = '!!SBtab SBtabVersion="0.8" Document="'+self.filename.rstrip('.xml')+'" TableType="Reaction" TableName="Reaction"\n!Reaction\t!Name\t!SumFormula\t!Location\t!Modifier\t!KineticLaw\t!SBOTerm\t!IsReversible\n'

        for reaction in self.model.getListOfReactions():
            value_row  = reaction.getId()+'\t'
            value_row += reaction.getName()+'\t'
            value_row += self.makeSumFormula(reaction)+'\t'
            try: compartment = reaction.getCompartment()+'\t'
            except: compartment = '\t'
            #try: value_row += reaction.getCompartment()+'\t'
            #except: value_row += '\t'
            modifiers = reaction.getListOfModifiers()
            if len(modifiers)>1:
                modifier_list = ''
                for i,modifier in enumerate(modifiers):
                    if i != len(reaction.getListOfModifiers())-1: modifier_list += modifier.getSpecies() + '|'
                    else: modifier_list += modifier.getSpecies() + '\t'
                value_row += modifier_list
            elif len(modifiers)==1:
                for modifier in modifiers: value_row += modifier.getSpecies()+'\t'
            else: value_row += '\t'
            try: kinlaw = reaction.getKineticLaw().getFormula()
            except: kinlaw = ''
            if kinlaw == '': kinlaw = ''
            value_row += kinlaw+'\t'          
            #try: value_row += reaction.getKineticLaw().getName()+'\t'
            #except: value_row += '\t'
            if str(reaction.getSBOTerm()) == '-1': value_row += '\t'
            else: str(reaction.getSBOTerm())+'\t'
            #try: value_row += str(reaction.getSBOTerm())+'\t'
            #except: value_row += '\t'
            try: value_row += str(reaction.getReversible())+'\n'
            except: value_row += '\t\n'
            reaction_SBtab += value_row

        return [reaction_SBtab,'reaction']

    def quantitySBtab(self):
        '''
        builds a Quantity SBtab
        '''
        quantity_SBtab = '!!SBtab SBtabVersion="0.8" Document="'+self.filename.rstrip('.xml')+'" TableType="Quantity" TableName="Quantity"\n!Quantity\t!SBML:parameter:id\t!Value\t!Unit\t!Description\n'

        for reaction in self.model.getListOfReactions():
            kinetic_law = reaction.getKineticLaw()
            if kinetic_law:
                value_row   = ''
                for parameter in kinetic_law.getListOfParameters():
                    value_row += parameter.getId()+'_'+reaction.getId()+'\t'
                    value_row += parameter.getId()+'\t'
                    value_row += str(parameter.getValue())+'\t'
                    try: value_row += parameter.getUnits()+'\t'
                    except: value_row += '\t'
                    value_row += 'local parameter\t\n'
                quantity_SBtab += value_row

        for parameter in self.model.getListOfParameters():
            value_row = parameter.getId()+'\t'
            value_row += parameter.getId()+'\t'
            value_row += str(parameter.getValue())+'\t'            
            try: value_row += parameter.getUnits()+'\t'
            except: value_row += '\t'            
            value_row += 'global parameter\t\n'
            quantity_SBtab += value_row
            
        return [quantity_SBtab,'quantity']

    def makeSumFormula(self,reaction):
        '''
        generates the sum formula of a reaction from the list of products and list of reactants
        '''
        sumformula = ''
        id2name    = {}
        
        for species in self.model.getListOfSpecies():
            id2name[species.getId()] = species.getName()

        for i,reactant in enumerate(reaction.getListOfReactants()):
            if i != len(reaction.getListOfReactants())-1:
                if reactant.getStoichiometry() != 1.0:
                    sumformula += str(int(reactant.getStoichiometry())) + ' ' + reactant.getSpecies()+' + '
                else:
                    sumformula += reactant.getSpecies()+' + '
            else:
                if numpy.isnan(reactant.getStoichiometry()):
                    sumformula += '1 ' + reactant.getSpecies() + ' <=> '
                elif reactant.getStoichiometry() != 1.0:
                    sumformula += str(int(reactant.getStoichiometry())) + ' ' + reactant.getSpecies()+' <=> '
                else:
                    sumformula += reactant.getSpecies()+' <=> '
        for i,product in enumerate(reaction.getListOfProducts()):
            if i != len(reaction.getListOfProducts())-1:
                if product.getStoichiometry() != 1.0:
                    sumformula += str(int(product.getStoichiometry())) + ' ' + product.getSpecies()+' + '
                else:
                    sumformula += product.getSpecies()+' + '
            else:
                if numpy.isnan(product.getStoichiometry()):
                    sumformula += '1 ' + product.getSpecies() + ' <=> '
                elif product.getStoichiometry() != 1.0:
                    sumformula += str(int(product.getStoichiometry())) + ' ' + product.getSpecies()+'\t'
                else:
                    sumformula += product.getSpecies()+'\t'
            
        #if there is no product in the reaction (e.g. influxes), don't forget the tab
        if len(reaction.getListOfProducts()) < 1:
            sumformula += '\t'

        return sumformula


if __name__ == '__main__':
    #sbml_model = open('BIOMD0000000061.xml','r')
    reader     = libsbml.SBMLReader()
    sbml_model = reader.readSBML('BIOMD0000000061.xml')
    sbml_class = SBMLDocument(sbml_model,'BIOMD.xml')

    print sbml_class.makeSBtabs()