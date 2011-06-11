#!/usr/bin/env python
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.

    @author: RaNaN
    @author: mkaay
"""

from module.PullEvents import UpdateEvent
from module.Progress import Progress
from module.utils import formatSize

from time import sleep, time

statusMap = {
    "finished":    0,
    "offline":     1,
    "online":      2,
    "queued":      3,
    "skipped":     4,
    "waiting":     5,
    "temp. offline": 6,
    "starting":    7,
    "failed":      8,
    "aborted":     9,
    "decrypting":  10,
    "custom":      11,
    "downloading": 12,
    "processing":  13,
    "unknown":     14,
}


def setSize(self, value):
    self._size = int(value)

class PyFile(object):
    def __init__(self, manager, id, url, name, size, status, error, pluginname, package, order):
        self.m = manager
        
        self.id = int(id)
        self.url = url
        self.name = name
        self.size = size
        self.status = status
        self.pluginname = pluginname
        self.packageid = package #should not be used, use package() instead
        self.error = error
        self.order = order
        # database information ends here
        
        self.plugin = None
        #self.download = None
            
        self.waitUntil = 0 # time() + time to wait
        
        # status attributes
        self.active = False #obsolete?
        self.abort = False
        self.reconnected = False
        
        self.progress = Progress()
        if self.status in (0, 4):
            self.progress.setValue(100)
        
        self.progress.notify = self.notifyChange

        self.m.cache[int(id)] = self


    # will convert all sizes to ints
    size = property(lambda self: self._size, setSize)
        
    def __repr__(self):
        return "PyFile %s: %s@%s" % (self.id, self.name, self.pluginname)

    def initPlugin(self):
        """ inits plugin instance """
        if not self.plugin:
            self.pluginmodule = self.m.core.pluginManager.getPlugin(self.pluginname)
            self.pluginclass = getattr(self.pluginmodule, self.m.core.pluginManager.getPluginName(self.pluginname))
            self.plugin = self.pluginclass(self)
    
    
    def package(self):
        """ return package instance"""
        return self.m.getPackage(self.packageid)

    def setStatus(self, status):
        self.status = statusMap[status]
        if self.status in (0, 4):
            self.progress.setValue(100)
        self.sync() #@TODO needed aslong no better job approving exists
    
    def hasStatus(self, status):
        return statusMap[status] == self.status
    
    def sync(self):
        """sync PyFile instance with database"""
        self.m.updateLink(self)

    def release(self):
        """sync and remove from cache"""
        self.sync()

        if hasattr(self, "plugin") and self.plugin:
            self.plugin.clean()
            del self.plugin
        if hasattr(self.progress, "notify"):
            del self.progress.notify
            self.progress.notify = None

        self.m.releaseLink(self.id)

    def delete(self):
        """delete pyfile from database"""
        self.m.deleteLink(self.id)

    def toDict(self):
        """return dict with all information for interface"""
        return self.toDbDict()

    def toDbDict(self):
        """return data as dict for databse

        format:

        {
            id: {'url': url, 'name': name ... }
        }

        """
        return {
            self.id: {
                'id': self.id,
                'url': self.url,
                'name': self.name,
                'plugin': self.pluginname,
                'size': self.getSize(),
                'format_size': self.formatSize(),
                'status': self.status,
                'statusmsg': self.m.statusMsg[self.status],
                'package': self.packageid,
                'error': self.error,
                'order': self.order,
                'progress': self.progress.getPercent(),
            }
        }
    
    def abortDownload(self):
        """abort pyfile if possible"""
        while self.id in self.m.core.threadManager.processingIds():
            self.abort = True
            if self.plugin and self.plugin.req:
                self.plugin.req.abortDownloads()
            sleep(0.1)
        
        self.abort = False
        if hasattr(self, "plugin") and self.plugin and self.plugin.req:
            self.plugin.req.abortDownloads()
        self.release()
        
    def finishIfDone(self):
        """set status to finish and release file if every thread is finished with it"""

        if self.id in self.m.core.threadManager.processingIds():
            return False
        
        self.setStatus("finished")
        self.release()
        return True
    
    def formatWait(self):
        """ formats and return wait time in humanreadable format """
        seconds = self.waitUntil - time()
        
        if seconds < 0: return "00:00:00"
                
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return "%.2i:%.2i:%.2i" % (hours, minutes, seconds)
    
    def formatSize(self):
        """ formats size to readable format """
        return formatSize(self.getSize())

    def formatETA(self):
        """ formats eta to readable format """
        seconds = self.getETA()
        
        if seconds < 0: return "00:00:00"
                
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return "%.2i:%.2i:%.2i" % (hours, minutes, seconds)
    
    def getSpeed(self):
        """ calculates speed """
        try:
            return self.plugin.req.speed
        except:
            return 0
        
    def getETA(self):
        """ gets established time of arrival"""
        try:
            return self.getBytesLeft() / self.getSpeed()
        except:
            return 0
    
    def getBytesLeft(self):
        """ gets bytes left """
        try:
            return self.plugin.req.size - self.plugin.req.arrived
        except:
            return 0
    
    def getPercent(self):
        """ get % of download """
        try:
            return self.plugin.req.percent
        except:
            return 0
        
    def getSize(self):
        """ get size of download """
        try:
            if self.plugin.req.size:
                return self.plugin.req.size
            else:
                return self.size
        except:
            return self.size
                
    def notifyChange(self):
        e = UpdateEvent("file", self.id, "collector" if not self.package().queue else "queue")
        self.m.core.pullManager.addEvent(e)
