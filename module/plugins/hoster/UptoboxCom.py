# -*- coding: utf-8 -*-

from module.plugins.internal.XFSHoster import XFSHoster, create_getInfo


class UptoboxCom(XFSHoster):
    __name__    = "UptoboxCom"
    __type__    = "hoster"
    __version__ = "0.26"
    __status__  = "testing"

    __pattern__ = r'https?://(?:www\.)?(uptobox|uptostream)\.com/\w{12}'
    __config__  = [("activated"   , "bool", "Activated"                                        , True ),
                   ("use_premium" , "bool", "Use premium account if available"                 , True ),
                   ("fallback"    , "bool", "Fallback to free download if premium fails"       , True ),
                   ("chk_filesize", "bool", "Check file size"                                  , False),
                   ("max_wait"    , "int" , "Reconnect if waiting time is greater than minutes", 10   )]

    __description__ = """Uptobox.com hoster plugin"""
    __license__     = "GPLv3"
    __authors__     = [("Benbox69", "dev@tollet.me")]


    PLUGIN_DOMAIN = "uptobox.com"

    INFO_PATTERN         = r'"para_title">(?P<N>.+) \((?P<S>[\d.,]+) (?P<U>[\w^_]+)\)'
    OFFLINE_PATTERN      = r'>(File not found|Access Denied|404 Not Found)'
    TEMP_OFFLINE_PATTERN = r'>Service Unavailable'

    LINK_PATTERN = r'"(https?://\w+\.uptobox\.com/d/.*?)"'

    DL_LIMIT_PATTERN = r'>You have to wait (.+) to launch a new download<'

    def check_filesize(self, file_size, size_tolerance=1024000):
        """
        Checks the file size of the last downloaded file
        :param file_size: expected file size
        :param size_tolerance: size check tolerance
        """
        if not self.last_download:
            return
    
        dl_location = encode(self.last_download)
        dl_size     = os.stat(dl_location).st_size
                          
        if dl_size < 1:
            self.fail(_("Empty file"))

        elif file_size > 0:
            diff = abs(file_size - dl_size)

            if diff > size_tolerance:
                self.log_info(_("File size mismatch | Expected file size: %s | Downloaded file size: %s")
                          % (file_size, dl_size))

            elif diff != 0:
                self.log_warning(_("File size is not equal to expected size"))

    def setup(self):
        self.multiDL = True
        self.chunk_limit = 1
        self.resume_download = True


getInfo = create_getInfo(UptoboxCom)
