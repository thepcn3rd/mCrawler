#!/usr/bin/python

import cmd
import requests
import re

# Global Variables

emailRE = re.compile("[A-Za-z0-9-_\.]+@[A-Za-z0-9]+\.[a-zA-Z]{2,5}")
urlRE = re.compile("(?:http\:\/\/|https\:\/\/|)[A-Za-z0-9-_\.]+\.[a-zA-Z]{2,5}")
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
            if not webPage.group(0) in listCurrentPages and not webPage.group(0) in url:
                listCurrentPages.append(webPage.group(0))
        if emailRE.search(line) is not None:
            email = emailRE.search(line)
            if not email.group(0) in listCurrentEmails:
                listCurrentEmails.append(email.group(0))
    print "Pages Collected"
    print "---------------"
    for i in range(0, len(listCurrentPages)):
        print listCurrentPages[i]
        if not "http" in listCurrentPages[i]:
            newURL = "http://" + domain + "/" + listCurrentPages[i]
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
        # print "Which Domain are we crawling (ie. scriptkitty.work)"
        # self.domain = raw_input("? ")
        self.domain = "scriptkitty.work"
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

    def do_changeURL(self, newURL):
        'Change the current URL manually'
        global urlRE
        if urlRE.match(newURL):
            self.url = newURL.lower()
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
            print "D. Display HTML Content of Current URL"
            print "E. Edit a URL from the List"
            print "R. Remove a URL from the List"
            print "Q. Stop Crawling Loop"
            selection = raw_input("Select the URL by the preceeding number: ")
            if selection in currentIDs:
                self.url = listURLs[int(selection)]
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
        'Saves the Emails that are in a Cache to a File (will overwrite the file)'
        global listEmails
        if len(filename) > 0:
            f = open(filename, "w")
            for i in range(0, len(listEmails)):
                f.write(listEmails[i] + "\n")
            f.close()
            print "Saved the output to the following file: " + filename
        else:
            print "Invalid filename format."
            print "Usage: saveEmailCache <filename>"
            print
        return


def main():
    webCrawler().cmdloop()


if __name__ == '__main__':
    main()
