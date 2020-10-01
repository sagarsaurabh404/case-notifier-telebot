import requests
import bs4 as bs4
import json
import typing
import sys
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)



URL = 'https://karnatakajudiciary.kar.nic.in/websitenew/causelist/causelist_Search.php'
page = requests.get(URL)
soup = bs4.BeautifulSoup(page.content, 'html.parser')



def get_data():
    cases = soup.findAll("td", id="casetd")
    all_data = []
    for case in cases:
        obj={
            'date': case.parent.find_previous('th').get_text(strip=True).split('THE')[2].rsplit(' ', 1)[0],
            'court_hall_num': case.parent.find_previous('th').parent.next_sibling.next_sibling.next_element.get_text(strip=True).split('LIST NO :')[0],
            'cause_list_num': case.parent.find_previous('th').parent.next_sibling.next_sibling.next_element.get_text(strip=True).split('LIST NO :')[1],
            'justice': " & ".join(case.parent.find_previous('th').parent.next_sibling.next_element.get_text(strip=True).split('&')),
            'case_no': case.get_text(strip=True), 
            'petitioner': case.next_sibling.next_sibling.get_text(strip=True), 
            'respondent': case.next_sibling.next_sibling.next_sibling.get_text(strip=True),
            'sl_no': case.parent.next_element.get_text(strip=True)
        }
        all_data.append(obj) 
    return all_data

def get_case_details(case_id, cause_list):
    case_obj = {}
    for cause in cause_list:
        if case_id.lower() in cause['case_no'].lower():
            case_obj = {
            'date': cause['date'],
            'court_hall_num': cause['court_hall_num'],
            'cause_list_num': cause['cause_list_num'],
            'justice': cause['justice'],
            'case_no': cause['case_no'], 
            'petitioner': cause['petitioner'], 
            'respondent': cause['respondent'],
            'sl_no': cause['sl_no']
            }
    return case_obj
        

def dump_data(data):
    with open('response.json', 'w') as out:
        out.write(json.dumps(data))

def get_assignment(name, cause_list):
    assignment_response = []
    _response_ = {}
    for cause in cause_list:
        if name.lower() in cause['petitioner'].lower() or name in cause['respondent'].lower() or name in cause['justice'].lower():
            _response_ = {
            'date': cause['date'],
            'court_hall_num': cause['court_hall_num'],
            'cause_list_num': cause['cause_list_num'],
            'justice': cause['justice'],
            'case_no': cause['case_no'], 
            'petitioner': cause['petitioner'], 
            'respondent': cause['respondent'],
            'sl_no': cause['sl_no']
            }
    if len(_response_)>0:
        assignment_response.append(_response_)
    return assignment_response

def main(param):

    # argv = sys.argv[1:]
    # key = argv[0].split(":")[0]
    # key_value = argv[0].split(":")[1]

    key = param.split(":")[0]
    key_value = param.split(":")[1]
    
    data = get_data()
    # logger.info(data)

    if 'case_id' in key:
        logger.info('fetching case details for: ' + key_value)
        return get_case_details(case_id=key_value, cause_list=data)
    elif 'name' in key:
        logger.info('fetching all cases for: ' + key_value)
        return get_assignment(name=key_value, cause_list=data)
    else:
        return "Oops! I did not get that. Please try again"

    
    

# if __name__ == '__main__':
#     main()