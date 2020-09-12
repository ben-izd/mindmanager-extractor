import zipfile, copy, sys, os
from bs4 import BeautifulSoup

archive_file_name = str(__file__.split('\\')[0])


def myquit():
    print('\n-- developer: beny74483@gmail.com --\n')
    input('Press any key to exit...')
    quit()


class_name:str = ''

# used to rsetore program state after some errors
if len(sys.argv) > 1:
    class_name = sys.argv[1]
else:
    class_name = input('\nType your class name: (press enter for default: "Question")\n-> ')
    print('')
    if class_name == '':
        class_name = 'Question'


class extract_from_mindmap_file:
    def __init__(self,file_name:str):
        self.file_name = os.path.splitext(file_name)[0]
        try:
            archive = zipfile.ZipFile(file_name, 'r')
            r = archive.read('Document.xml').decode()
            archive.close()
        except:
            print('Unknown error while opening file...')
            myquit()

    
        r_copy = copy.copy(r)
        
        self.b = BeautifulSoup(r, 'xml')
        

        # get all topics - filter duplicates
        self.topics = filter(lambda x: x.findChildren(
            "Text", recursive=False), self.b.find('OneTopic').findAll('Topic'))



        # regenerate ids for topics
        for index, topic in enumerate(self.topics, start=1):
            
            r_copy = r_copy.replace(topic['OId'],str(index))

        # recalculate variables
        self.b = BeautifulSoup(r_copy, 'xml')

        self.topics = list(filter(lambda x: x.findChildren(
            "Text", recursive=False), self.b.find('OneTopic').findAll('Topic')))


    def get_text(self,element):
        # get element text
        if element is None:
            return ''
        return element.find('Text')['PlainText']


    def find_topic(self,topic_id):
        # find topic by id
        return self.b.find('Topic', {'OId': topic_id})


    def find_topic_text(self,topic_id):
        return self.get_text(self.find_topic(topic_id=topic_id))


    def base_id(self,element):
        # get the base element id
        return element.find('ObjectReference')['OIdRef']


    def target_id(self,element):
        # get the target element id
        return element.findAll('ObjectReference')[1]['OIdRef']


    def find_relationships(self,base_id_filter: list = None, target_id_filter: list = None):
        # find all relationship + filtering by id
        rels = self.b.findAll('Relationship')
        if base_id_filter:
            rels = [i for i in rels if self.base_id(i) in base_id_filter]
        if target_id_filter:
            rels = [i for i in rels if self.target_id(i) in target_id_filter]
        return rels

    def find_links(self,topic_id: str):
        # find all relationship that match it's base id to topic_id
        temp_children = self.find_relationships(base_id_filter=[topic_id])
        res_texts = []
        res_links = []
        for i in temp_children:
            res_links.append(int(self.target_id(i)))
            res_texts.append(self.get_text(i))
        return res_texts, res_links

    # filter obejcts that are nested to each other which result in repetitve elements by searching 'topic'

    def to_string(self):
        # make result printable
        result = ''
        for index,topic in enumerate(list(self.topics)):
            temp = self.find_links(topic['OId'])
            end =',\n'
            
            if index==len(self.topics)-1:
                end = ''

            result += f"{class_name}({topic['OId']}, '{self.get_text(topic)}', {temp[0]}, {temp[1]}){end}"
        return result

    def save_to_disk(self):
        # save result file same name as opened file but with 'txt' format
        result_file_name = self.file_name+'.txt'

        # check wether is there any file similar to result file name
        if os.path.exists(result_file_name):
            print(f'ERROR - Could not save the result file - there is already a "{result_file_name}" file in the directory')
            myquit()
        try:
            with open(result_file_name,'w') as file:
                file.write(self.to_string())
            print(f'Result file ("{result_file_name}") saved successfully.')
        except:
            print(f'Counter error while saving "{result_file_name}" to disk...')
            print('Retry or apply it on a copy of your file\n')


target_file_name = input('Type Mind Manager file name with extension (like "1.mmap"):\n-> ')
print('')
if os.path.exists(target_file_name) == False:
    print('ERROR - either you enter invalid file name or the file is not in the directory holds this file\n')
    os.system(f'python {archive_file_name} {class_name}')
    quit()

a = extract_from_mindmap_file(target_file_name)
a.save_to_disk()

myquit()

