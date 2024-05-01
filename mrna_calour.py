import requests
import webbrowser
from logging import getLogger

from calour.util import get_config_value
from calour.database import Database

logger = getLogger(__name__)


class mRNA(Database):
    def __init__(self, exp=None):
        super().__init__(database_name='mRNA', methods=['get'])

        # Web address of the gene information sever server
        # we use the harmonizome server from the Avi Ma'ayan lab ( https://labs.icahn.mssm.edu/maayanlab/ )
        # based on the publication:
        # Rouillard AD, Gundersen GW, Fernandez NF, Wang Z, Monteiro CD, McDermott MG, Ma'ayan A. The harmonizome: a collection of processed datasets gathered to serve and mine knowledge about genes and proteins. Database (Oxford). 2016 Jul 3;2016. pii: baw100.

        self.dburl = self._get_db_address()
        self.web_interface = 'https://maayanlab.cloud/Harmonizome'

    def _get_db_address(self):
        '''
        Get the database 

        Returns
        -------
        server_address : str
            the harmonizome server web address
        '''
        server_address = 'https://maayanlab.cloud/Harmonizome/api/1.0'
        logger.debug('using Harmonizome server %s' % server_address)
        return server_address

    def _post(self, api, rdata):
        '''POST a request to the mRNA database

        Parameters
        ----------
        api : str
            the REST API address to post the request to
        rdata : dict
            parameters to pass to the dbBact REST API

        Returns
        -------
        res : request
            the result of the request
        '''
        res = requests.post(self.dburl + '/' + api, json=rdata)
        if res.status_code != 200:
            logger.warn('REST error %s enountered when accessing mRNA database %s: %s' % (res.reason, api, res.content))
        return res

    def _get(self, api, rdata=None):
        '''GET a request to the mRNA database

        Parameters
        ----------
        api : str
            the REST API address to post the request to
        rdata : dict
            parameters to pass to the dbBact REST API

        Returns
        -------
        res : request
            the result of the request
        '''
        if rdata is None:
            res = requests.get(self.dburl + '/' + api)
        else:
            res = requests.get(self.dburl + '/' + api, json=rdata)
        if res.status_code != 200:
            logger.warn('REST error %s enountered when accessing mRNA database %s: %s' % (res.reason, api, res.content))
        return res

    def get_annotation_string(self, info):
        '''Get nice string summaries of annotations

        Parameters
        ----------
        info : dict (see get_sequence_annotations)

        Returns
        -------
        desc : list of str
            a short summary of each annotation, sorted by importance
        '''
        desc = []
        for ck,cv in info.items():
            desc.append('%s: %s' % (ck, cv))
        return desc
    
    def get_seq_annotations(self, sequence):
        '''Get the annotations for a gene name (sequence)

        Parameters
        ----------
        sequence : str
            The gene name to get the annotations for

        Returns
        -------
        annotations : list of list of (annotation dict,list of [Type,Value] of annotation details)
            See dbBact sequences/get_annotations REST API documentation
        term_info : dict of {term: info}
            where key (str) is the ontology term, info is a dict of details containing:
                'total_annotations' : total annotations having this term in the database
                'total_sequences' : number of annotations with this term for the sequence
        '''
        sequence = sequence.upper()
        res = self._get('gene/%s' % sequence)
        if res.status_code != 200:
            print('error')
            return []
        info = res.json()
        desc = self.get_annotation_string(info)
        return desc

    def get_seq_annotation_strings(self, sequence):
        '''Get nice string summaries of annotations for a given sequence

        Parameters
        ----------
        sequence : str
            the gene name to query the annotation strings about

        Returns
        -------
        shortdesc : list of (dict,str) (annotationdetails,annotationsummary)
            a list of:
                annotationdetails : dict
                    'seqid' : str, the sequence annotated
                    'annotationtype : str
                    ...
                annotationsummary : str
                    a short summary of the annotation
        '''
        shortdesc = []
        annotations = self.get_seq_annotations(sequence)
        for cann in annotations:
            shortdesc.append(({'annotationtype': 'other', 'sequence': sequence}, cann))
        return shortdesc

    def show_annotation_info(self, annotation):
        '''Show the website for the sequence

        Parameters
        ----------
        annotation : dict
            should contain 'sequence'
        '''
        # open in a new tab, if possible
        new = 2

        address = '%s/gene/%s' % (self.web_interface, annotation['sequence'])
        webbrowser.open(address, new=new)
