def getResultInFormat(location, title, url, date):
    return '지역:' + location + '\n' + '제목: ' + title + '\n' + '링크': + url + '\n' + '날짜:' +  date.strftime('%m-%d') + '\n*************************************'