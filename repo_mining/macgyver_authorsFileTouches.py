import json
import requests
import csv

import os

if not os.path.exists("data"):
 os.makedirs("data")

# GitHub Authentication function
def github_auth(url, lsttoken, ct):
    jsonData = None
    try:
        ct = ct % len(lstTokens)
        headers = {'Authorization': 'Bearer {}'.format(lsttoken[ct])}
        request = requests.get(url, headers=headers)
        jsonData = json.loads(request.content)
        ct += 1
    except Exception as e:
        pass
        print(e)
    return jsonData, ct

# @dictFiles, empty dictionary of files
# @lstTokens, GitHub authentication tokens
# @repo, GitHub repo
def countfiles(dictfiles, lsttokens, repo, file_extension_list, knownFileBase):
    ipage = 1  # url page counter
    ct = 0  # token counter

    try:
        # loop though all the commit pages until the last returned empty page
        while True:
            spage = str(ipage)
            commitsUrl = 'https://api.github.com/repos/' + repo + '/commits?page=' + spage + '&per_page=100'
            jsonCommits, ct = github_auth(commitsUrl, lsttokens, ct)

            # break out of the while loop if there are no more commits in the pages
            if len(jsonCommits) == 0:
                break
            # iterate through the list of commits in  spage
            for shaObject in jsonCommits:
                sha = shaObject['sha']
                # For each commit, use the GitHub commit API to extract the files touched by the commit
                shaUrl = 'https://api.github.com/repos/' + repo + '/commits/' + sha
                shaDetails, ct = github_auth(shaUrl, lsttokens, ct)
                filesjson = shaDetails['files']
                authorName = shaDetails['commit']['author']['name']
                date = shaDetails['commit']['author']['date']

                for filenameObj in filesjson:
                    filename = filenameObj['filename']
                    # check if source file
                    push_to_dictionary = False
                    for ext in file_extension_list:
                        if ext in filename:
                            push_to_dictionary = True
                            break
                    
                    # check if doesnt exists and push
                    if push_to_dictionary == True:
                        knownFileBase.append((filename, authorName, date))
                        #print(authorName + date + filename)

                    dictfiles[filename] = dictfiles.get(filename, 0) + 1
                    #print(filename)
            ipage += 1
    except:
        print("Error receiving data")
        exit(0)
# GitHub repo
repo = 'scottyab/rootbeer'
# repo = 'Skyscanner/backpack' # This repo is commit heavy. It takes long to finish executing
# repo = 'k9mail/k-9' # This repo is commit heavy. It takes long to finish executing
# repo = 'mendhak/gpslogger'


# put your tokens here
# Remember to empty the list when going to commit to GitHub.
# Otherwise they will all be reverted and you will have to re-create them
# I would advise to create more than one token for repos with heavy commits
lstTokens = ["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"]

file_extension_list = [".java", ".kt", ".cpp", "c", ".h", "CMakeLists.txt"]

# Key author, Value dict date string array
knownFileBase = []

dictfiles = dict()
countfiles(dictfiles, lstTokens, repo, file_extension_list, knownFileBase) #### MAIN FUNCTION

print('Total number of authors: ' + str(len(knownFileBase)))
print('Total number of files: ' + str(len(dictfiles)))

file = repo.split('/')[1]
# change this to the path of your file
fileOutput = 'data/file_' + file + '.csv'
rows = ["Filename", "Author", "Timestamp"]
fileCSV = open(fileOutput, 'w')
writer = csv.writer(fileCSV)
writer.writerow(rows)

bigcount = None
bigfilename = None
for filename, author, timestamp in knownFileBase:
    rows = [filename, author, timestamp]
    writer.writerow(rows)

fileCSV.close()

#for filename, count in dictfiles.items():
#    rows = [filename, count]
#    writer.writerow(rows)
#    if bigcount is None or count > bigcount:
#        bigcount = count
#        bigfilename = filename
#fileCSV.close()
#print('The file ' + bigfilename + ' has been touched ' + str(bigcount) + ' times.')
