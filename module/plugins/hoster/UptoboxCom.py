# -*- coding: utf-8 -*-

from module.plugins.internal.XFSHoster import XFSHoster, create_getInfo


class UptoboxCom(XFSHoster):
    __name__    = "UptoboxCom"
    __type__    = "hoster"
    __version__ = "0.26"
    __status__  = "testing"

    __pattern__ = r'https?://(?:www\.)?(uptobox|uptostream)\.com/\w{12}'
    __config__  = [("activated"      , "bool", "Activated"                                        , True     ),
                   ("use_premium"    , "bool", "Use premium account if available"                 , True     ),
                   ("fallback"       , "bool", "Fallback to free download if premium fails"       , True     ),
                   ("chk_filesize"   , "bool", "Check file size"                                  , True     ),
                   ("max_wait"       , "int" , "Reconnect if waiting time is greater than minutes", 10       ),
                   ("size_tolerance" , "int" , "Tolerance is used when comparing displayed size"  , 104857600)]

    __description__ = """Uptobox.com hoster plugin"""
    __license__     = "GPLv3"
    __authors__     = [("Benbox69", "dev@tollet.me")]


    PLUGIN_DOMAIN = "uptobox.com"

    INFO_PATTERN         = r'"para_title">(?P<N>.+) \((?P<S>[\d.,]+) (?P<U>[\w^_]+)\)'
    OFFLINE_PATTERN      = r'>(File not found|Access Denied|404 Not Found)'
    TEMP_OFFLINE_PATTERN = r'>Service Unavailable'

    LINK_PATTERN = r'"(https?://\w+\.uptobox\.com/d/.*?)"'

    DL_LIMIT_PATTERN = r'>You have to wait (.+) to launch a new download<'
            
    def setup(self):
        self.multiDL = True
        self.chunk_limit = 1
        self.resume_download = True


getInfo = create_getInfo(UptoboxCom)
