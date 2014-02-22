import bleach
import re

CLEAN_LEVEL_LOW = 0
CLEAN_LEVEL_MID = 5
CLEAN_LEVEL_HIGH = 10
CLEAN_LEVEL_STRIP = 99

CLEAN_LEVELS_INHERIT = {
    CLEAN_LEVEL_LOW   : [CLEAN_LEVEL_MID],
    CLEAN_LEVEL_MID   : [CLEAN_LEVEL_HIGH],
    CLEAN_LEVEL_HIGH  : [CLEAN_LEVEL_STRIP],
    CLEAN_LEVEL_STRIP : [],
}

CLEAN_LEVELS_TAGS = {
    CLEAN_LEVEL_LOW   : ['img', 'li', 'ol', 'ul'],
    CLEAN_LEVEL_MID   : ['p', 'div', 'a', 'b', 'em', 'i', 'u', 'strong'],
    CLEAN_LEVEL_HIGH  : ['br'],
    CLEAN_LEVEL_STRIP : [],
}
CLEAN_LEVELS_ATTRS = {
    CLEAN_LEVEL_LOW   : {},
    CLEAN_LEVEL_MID   : {'a': ['href', 'alt', 'target'], '*' : ['class', 'title']},
    CLEAN_LEVEL_HIGH  : {},
    CLEAN_LEVEL_STRIP : {},
}

br_re = re.compile('<br ?/?>')

def clean(html, level = CLEAN_LEVEL_MID):
    if not html:
        return ''
    
    tags = get_tags(level)
    attributes = get_attrs(level)
    
    if 'br' not in tags:
        html = br_re.sub(' ', html)
    
    return unicode(bleach.clean(html, 
                        tags = tags, 
                        attributes = attributes, 
                        strip = True)).strip()

def strip(html):
    return clean(html, level = CLEAN_LEVEL_STRIP)


def get_tags(level):
    levels = get_levels(level)
    tags = []
    
    for level in levels:
        tags.extend(CLEAN_LEVELS_TAGS[level])    
    
    return tags


def get_attrs(level):
    levels = get_levels(level)
    attrs = {}
    
    for level in levels:
        for tag, tag_attrs in CLEAN_LEVELS_ATTRS[level].items():

            if tag not in attrs:
                attrs[tag] = []

            attrs[tag].extend(tag_attrs)
    
    return attrs


def get_levels(level):
    levels = [level]
    
    for level in CLEAN_LEVELS_INHERIT[level]:
        levels.extend(get_levels(level))
        
    return levels

if __name__ == '__main__':
    from time import time
    
    reps = 1000
    s = '<p class="class-from-wywiwyg-or-smt">this is text<br /></p>but this too <br />'

    start = time()
    for i in range(0, reps):
        clean(s)
    timetaken = (time() - start)
    print "%d reps took %f, %f per rep" % (reps, timetaken, timetaken / reps)
    assert timetaken < 3.0
    
    assert 'img' in get_tags(CLEAN_LEVEL_LOW)
    assert 'class' in get_attrs(CLEAN_LEVEL_LOW)['*']
    
    tests = [   
             #text should work, brs are cleaned
            ('<p class="class-from-wywiwyg-or-smt">this is text<br /></p>but this too <br />', '<p class="class-from-wywiwyg-or-smt">this is text<br></p>but this too <br>'),
            # attributes should be removed
            ('<div onload="alert("Haha, I hacked your page.");">1</div>',  '<div>1</div>'),
            # make sure we cant exploit removal of tags
            ('<<script></script>script> alert("Haha, I hacked your page."); <<script></script>/script>', '&lt;script&gt; alert("Haha, I hacked your page."); &lt;/script&gt;'),
            # try the same trick with attributes, gives an Exception
            ('<div on<script></script>load="alert("Haha, I hacked your page.");">1</div>', '<div>load="alert("Haha, I hacked your page.");"&gt;1</div>'),
             # no tags should be skipped
            ('<script>bad</script><script>bad</script><script>bad</script>', 'badbadbad'),
            # leave valid tags but remove bad attributes
            ('<a href="good" onload="bad" onclick="bad" alt="good">1</div>', '<a alt="good" href="good">1</a>'),
    ]
    
    for text, out in tests:
        res = clean(text)
        assert res == out, "%s => %s != %s" % (text, res, out)
            
