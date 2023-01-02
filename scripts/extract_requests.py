import re
import sys




def main():

    try:
        path = sys.argv[1]
    except: 
        print('Error: Include path to the network log')
        return


    f = open(path, "r")

    logs = f.read()
    logs = re.split('\'\n|: \'', logs)

    # grab all requests made (includes the fuzzed/custom/candidate values)
    requests = []
    for i in range(len(logs)):
        if 'Sending' in logs[i]:
            requests.append('-> ' + logs[i+1] + '\n\n')

    # remove content-length and user-agent from the requests. RESTler automatically populates them so we must remove them
    updated = []
    for i in requests:
        req = i.split('\\r\\n')
        new_req = []
        for j in req:
            if not 'Content-Length' in j and not 'User-Agent' in j:
                new_req.append(j) 
                
        req = '\\r\\n'.join(new_req)
        updated.append(req)

    f = open("all_reqs_replay.txt", "w")
    string = ''.join(updated)
    string = string.replace('_OMITTED_AUTH_TOKEN_','AUTHORIZATION TOKEN')
    f.write(string)



if __name__ == "__main__":
    sys.exit(main())