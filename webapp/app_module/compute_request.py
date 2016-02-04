# This will be the main function for formulating a compute request. The compute request to compute engine is big and is basically a big dictionary.
# use the dictionary here to take in a

from collections import Mapping, Set, Sequence
import json
from apiclient.discovery import build
from app_module.name_generator.name_generator import word_gen
def get_path(dct, path):
    """ paths to nested json more sensibly """
    for list_index, dict_key in re.findall(r'(\d+)|(\w+)', path):
        dct = dct[dict_key or int(list_index)]
    return dct


# dual python 2/3 compatability, inspired by the "six" library
string_types = (str, unicode) if str is bytes else (str, bytes)
iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()

def objwalk(obj, path=(), memo=None):
    '''
    descend an object heirarchy and generate paths. A helper function
    http://code.activestate.com/recipes/577982-recursively-walk-python-objects/
    :param obj:
    :param path:
    :param memo:
    :return:
    '''
    if memo is None:
        memo = set()
    iterator = None
    if isinstance(obj, Mapping):
        iterator = iteritems
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        iterator = enumerate
    if iterator:
        if id(obj) not in memo:
            memo.add(id(obj))
            for path_component, value in iterator(obj):
                for result in objwalk(value, path + (path_component,), memo):
                    yield result
            memo.remove(id(obj))
    else:
        yield path

def pathmaker(obj_walk):
    '''
    concatenate objwalk into paths for find_path (period seperated lists)
    :param obj_walk:
    :return:
    '''
    out=[]
    for pth in objwalk(obj_walk):
        out.app
        end('.'.join([str(i) for i in pth]))
    return out

def findpath(obj,search_path):
    '''
    search through an object and return paths that contain a given key
    :param obj:
    :param search_path:
    :return:
    '''
    paths=pathmaker(obj)
    search=r'(.*{}.*)'.format(search_path)
    return [j[0] for j in [re.findall(search,i,flags=re.IGNORECASE) for i in paths] if j]

def json_load(x):
    with open(x,'rb') as f:
        out=json.load(f)
    return out

class ComputeRequest(object):
    '''
    the main class that creates and formats the compute request.
    May need to also generate params for creating the service to launch the request
    '''
    def __init__(self,template_path,project='ADMINPROJECT_PLACEHOLDER',zone='us-central1-f',**kwargs):
        """

        :type self: object
        """
        self.__request_template=json_load(template_path)
        self.__admin_project=project
        self.__zone=zone
        self.__prop_flags={}
        # self.request=json_load(template_path)
        self.properto=kwargs

    @property
    def request(self):
        """

        :type self: object
        """
        self.__request=self.__request_template
        if not self.__prop_flags.get('metadata'):
            self.__metadata_replace()
        self.__set_name()
        self.__set_machine_type()
        self.__set_disk_image()
        #TODO self.__set_disk_size()
        #TODO self.__set_tags()
        return self.__request

    def __metadata_replace(self):
        if self.properto.get('metadata'):
            [self.__request['metadata']['items'].append({'key':ke,'value':va}) for ke,va in self.properto['metadata'].items()]
            print self.__request['metadata']
        self.__prop_flags['metadata']=1
        return None

    def __set_name(self):
        """
        sets name or generates one if needed
        :return: none
        """
        if not self.properto.get("inst_name"):
            self.properto['inst_name']=word_gen()
        self.__request['name']=self.properto['inst_name']
        self.__request['disks'][0]['deviceName']=self.properto['inst_name']
        return None

    def __set_machine_type(self):
        '''
        sets machine type. Throws error if no type selected
        :return:
        '''
        if not self.properto.get("machine_type"):
            raise AttributeError('no machine type selected')
        self.__request['machineType']='zones/'+self.__zone+'/machineTypes/'+self.properto['machine_type']

    def __set_disk_image(self):
        # TODO ensure disk0 is bootdisk
        # bootdisk=[idx for i,idx in enumerate(self.__request['disks']) if i['boot']]
        if not self.properto.get("disk_image"):
            self.properto['disk_image']="projects/ADMINPROJECT_PLACEHOLDER/global/images/rstudio-server-deb"
        self.__request['disks'][0]['initializeParams']['sourceImage']=self.properto['disk_image']

    def execute(self,project='ADMINPROJECT_PLACEHOLDER',zone='us-central1-f',cred=None):
        '''
        executes compute instance based on given request
        :param project:
        should be left to ADMINPROJECT_PLACEHOLDER since that is where the usable rstudio image is located
        :param zone:
        defaults to us-central1-f override to us-central1-c or something else when needed (better machine types available)
        :return:
        returns status of request
        '''
        compute=build('compute','v1',credentials=cred.credentials)
        out=compute.instances().insert(project=project,zone=zone,body=self.request).execute()
        return out

class ComputeInfo(object):
    def __init__(self,project,zone,oauth2):
        self.__compute=build('compute','v1',credentials=oauth2.credentials)
        self.__project=project
        self.__zone=zone
        self.__oauth2=oauth2
    @property
    def compute_machine_types(self):
        mts=self.__compute.machineTypes().list(project=self.__project,zone=self.__zone).execute()
        # [mt for mt in mts['items']]
        return [{'name':mt['name'],'cpus':mt['guestCpus'],'mem_gb':round(float(mt['memoryMb'])/1024,2)} for mt in mts['items']]
    @property
    def compute_images(self):
        x=self.__compute.images().list(project=self.__project).execute()
        return [i for i in x['items']]
    @property
    def compute_instances(self):
        '''
        sets the list of compute instances currently running. Results are based on init values for the class regarding project and zone
        :return:
        '''
        #TODO error handling, make this more tolerant -- if anything is missing here, the whole function is going to throw an error
        self.__instances=self.__compute.instances().list(zone=self.__zone,project=self.__project).execute()
        if not 'items' in self.__instances:
            return []
        inst_list=self.__instances['items']
        out=[{"start_time":i['creationTimestamp'],
         'server_up':[j['value'] for j in i['metadata']['items'] if j['key'] == 'serverready'][0],
         'name':i['name'],
         'ipaddress':i['networkInterfaces'][0]['accessConfigs'][0]['natIP'],
         'MachineType':i['machineType'],
         'MachineType_short':i['machineType'].split('/')[-1],
         'status':i['status']
         } for i in inst_list]
        self.__instances_cached=out
        return out
