#!/usr/bin/python

import cmd
import requests
import re

# Global Variables

#emailRE = re.compile("[A-Za-z0-9-_\.]+@[A-Za-z0-9]+\.[a-zA-Z]{2,5}")
emailRE = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
#urlRE = re.compile("(?:http\:\/\/|https\:\/\/|)[A-Za-z0-9-_\.]+\.[a-zA-Z]{2,5}")
#urlRE = re.compile("(?:http\:\/\/|https\:\/\/|)(?:[a-zA-Z0-9-_\/]+|)[A-Za-z0-9-_\.]+\.[a-zA-Z]{2,5}")
#urlRE = re.compile(".*((href=|src=)(\x22|')(?P<url>[a-zA-Z0-9-_\.\/]+)(\x22|'))|((?P<urlFull>(http:\/\/|https:\/\/)[a-zA-Z0-9-_\.]{5,})).*")
#urlRE = re.compile("((href=|src=)(\x22|')(?P<url>[a-zA-Z0-9-_\.\/]+)(\x22|'))|((?P<urlFull>(http:\/\/|https:\/\/)[a-zA-Z0-9-_\.]{5,}))")
urlRE = re.compile("((href=|src=)(\x22|'|)(?P<url>(http:\/\/|https:\/\/|)[a-zA-Z0-9-_\.\/]+)(\x22|'|))|((?P<urlFull>(http:\/\/|https:\/\/)[a-zA-Z0-9-_\.]{5,}))")
# (?<url>(http:\/\/|https:\/\/)[a-zA-Z0-9-_\.]{5,}) (Standard URL Syntax)
# (href=|src=)("|')(?<url>[a-zA-Z0-9-_\.\/]+)("|') (Pulling pages out from between tags)
domainRE = re.compile("[a-zA-Z0-9-_\.]")
listEmails = []
listURLs = []
htmlContent = ""


def crawl(url, domain):
    global listEmails, listURLs, urlRE, htmlContent
    listCurrentEmails = []
    listCurrentPages = []
    page = requests.get(url)
    htmlContent = page.content
    for line in page.content.split('\n'):
        if urlRE.search(line) is not None:
            webPage = urlRE.search(line)
            if webPage.group('url') is not None:
                if not webPage.group('url') in listCurrentPages and not webPage.group('url') in url:
                    listCurrentPages.append(webPage.group('url'))
            if webPage.group('urlFull') is not None:
                if not webPage.group('urlFull') in listCurrentPages and not webPage.group('urlFull') in url:
                    listCurrentPages.append(webPage.group('urlFull'))
        if emailRE.search(line) is not None:
            email = emailRE.search(line)
            if not email.group(0) in listCurrentEmails:
                listCurrentEmails.append(email.group(0))
    print "Pages Collected"
    print "---------------"
    for i in range(0, len(listCurrentPages)):
        print listCurrentPages[i]
        if not "http" in listCurrentPages[i]:
            # If the URL begins with a slash remove it to avoid double slashes in a URL
            if listCurrentPages[i][:1] == "/":
                listCurrentPages[i] = listCurrentPages[i][1:]
            newURL = "http://" + domain + "/" + listCurrentPages[i]
            if not newURL in listURLs:
                listURLs.append(newURL)
        else:
            newURL = listCurrentPages[i]
            if not newURL in listURLs:
                listURLs.append(newURL)
    print
    print "Emails Collected from this Page"
    print "-------------------------------"
    for j in range(0, len(listCurrentEmails)):
        print listCurrentEmails[j]
        if not listCurrentEmails[j] in listEmails:
            listEmails.append(listCurrentEmails[j])
    print
    print "Current URL: " + url
    print
    raw_input("Press any key to continue...")
    print


class webCrawler(cmd.Cmd):
    def __init__(self):
        print
        print "This web crawler is designed to allow you to manually crawl through a site."
        print "As it crawls it will extract urls and email addresses based on regular expressions."
        print "You can modify the regular expressions that are searched for as you crawl."
        print
        print "Which Domain are we crawling (ie. scriptkitty.work)"
        self.domain = raw_input("? ")
        #self.domain = "scriptkitty.work"
        secureURL = raw_input("Is the domain a secure site? ")
        if secureURL == 'y' or secureURL == 'Y':
            self.url = "https://" + self.domain
        else:
            self.url = "http://" + self.domain
        print
        crawl(self.url, self.domain)
        print
        print "To begin crawling manually type: selectURL"
        print
        cmd.Cmd.__init__(self)
        self.prompt = "#> "

    def emptyline(self):
        pass

    def do_quit(self, arg):
        'Quit out of the crawler'
        return True

    def do_recrawl(self, input):
        'Recrawls the current URL'
        crawl(self.url, self.domain)
        return

    def do_crawl(self, input):
        'Recrawls the current URL'
        crawl(self.url, self.domain)
        return

    def do_changeDomain(self, newDomain):
        'Change the current URL manually'
        global domainRE
        if domainRE.match(newDomain):
            self.domain = newDomain.lower()
            secureURL = raw_input("Is the domain a secure site? ")
            if secureURL == 'y' or secureURL == 'Y':
                self.url = "https://" + self.domain
            else:
                self.url = "http://" + self.domain
        else:
            print "Incorrect format based on the regular expression provided."
            print "Syntax: changeURL http://scriptkitty.work"
            print
        return

    def do_selectURL(self, input):
        'Select a URL from the list collected that has not been crawled...'
        global listURLs, htmlContent
        while True:
            currentIDs = []
            print
            print "Select URL to Crawl Next"
            print "------------------------"
            for i in range(0, len(listURLs)):
                print str(i) + ": " + listURLs[i]
                currentIDs.append(str(i))
            print
            print "Current URL: " + self.url
            print
            print "C. Crawl Current URL"
            print "D. Display HTML Content of Current URL"
            print "E. Edit a URL from the List"
            print "R. Remove a URL from the List"
            print "Q. Stop Crawling Loop"
            selection = raw_input("Select the URL by the preceeding number: ")
            if selection in currentIDs:
                self.url = listURLs[int(selection)]
                crawl(self.url, self.domain)
            elif selection == "c" or selection == "C":
                crawl(self.url, self.domain)
            elif selection == "d" or selection == "D":
                print htmlContent
                print
                raw_input("Press any key to continue...")
            elif selection == "e" or selection == "E":
                editSelection = raw_input("URL to Edit (Select by preceeding number): ")
                if editSelection in currentIDs:
                    print "Editing the following URL: " + listURLs[int(editSelection)]
                    newURL = raw_input("New URL: ")
                    listURLs[int(editSelection)] = newURL
                else:
                    print "Invalid URL Selection to Edit"
            elif selection == "r" or selection == "R":
                delSelection = raw_input("URL to Delete (Select from preceeding number): ")
                if delSelection in currentIDs:
                    listURLs.remove(listURLs[int(delSelection)])
            elif selection == 'q' or selection == 'Q':
                break
            else:
                continue
        return

    def do_displayURL(self, input):
        'Display the current URL'
        print "Current URL: " + self.url
        return

    def do_flushEmailCache(self, input):
        'Flushes the Cache of Emails Collected from Pages'
        global listEmails
        listEmails = []
        return

    def do_flushURLCache(self, input):
        'Flushes the Cache of URLs Collected from Pages'
        global listURLs
        listURLs = []
        return

    def do_saveEmailCache(self, filename):
        'Saves the Emails that are in the Cache to a File (will overwrite the file)'
        global listEmails
        if len(filename) > 0:
            fPath = "output/" + filename
            f = open(fPath, "w")
            for i in range(0, len(listEmails)):
                f.write(listEmails[i] + "\n")
            f.close()
            print "Saved the output to the following file: " + fPath
        else:
            print "Invalid filename format."
            print "Usage: saveEmailCache <filename>"
            print
        return

    def do_saveURLCache(selfself, filename):
        'Saves the URLs that are in the Cache to a File (will overwrite the file)'
        global listURLs
        if len(filename) > 0:
                fPath = "output/" + filename
                f = open(fPath, "w")
                for i in range(0, len(listURLs)):
                    f.write(listURLs[i] + "\n")
                f.close()
                print "Saved the output to the following file: " + fPath
        else:
                print "Invalid filename format."
                print "Usage: saveURLCache <filename>"
                print
        return

    def do_showEmailCache(self, input):
        'Shows the contents of the email cache.'
        global listEmails
        print "Email Cache"
        print "-----------"
        for i in range(0, len(listEmails)):
            print listEmails[i]
        print
        return

    def do_showURLCache(self, input):
        'Shows the contents of the URL cache.'
        global listURLs
        print "URL Cache"
        print "---------"
        for i in range(0, len(listURLs)):
            print listURLs[i]
        print
        return



def main():
    webCrawler().cmdloop()


if __name__ == '__main__':
    main()
