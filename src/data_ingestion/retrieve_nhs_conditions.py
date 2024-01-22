# use NHS UK conditions api (https://api.nhs.uk/conditions) to retrieve all of the conditions listed there to use for RAG

import requests

# get all conditions from NHS UK api
def call_nhs_uk_api(url="https://api.nhs.uk/conditions/", headers={'subscription-key': None,'accept': "application/json"}):
    response = requests.request("GET", url, headers=headers)

    return response.json()

    # this needs to loop over all the pages
    # for each page it needs to go through each of the conditions in "significantLink" and getting the URL and name
    # these URLs then need to be accessed, and the full text of the website needs to be retrieved

if __name__ == "__main__":
    conditions = call_nhs_uk_api()
    print(conditions['significantLink'])