"Simple parser for Garmin TCX files."
import sys
import time
from lxml import objectify, etree

namespace = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'

class TCXParser:

    def __init__(self, tcx_file):
        tree = objectify.parse(tcx_file)
        self.root = tree.getroot()
        self.activity = self.root.Activities.Activity
        self._distance = self.get_distance()
        
        
    def hr_values(self):
        return [int(x.text) for x in self.root.xpath('//ns:HeartRateBpm/ns:Value', namespaces={'ns': namespace})]

    def positions(self):
        #return [(x.Time, x.Position) for x in self.root.xpath('//ns:Trackpoint', namespaces={'ns': namespace})]
        #return [(etree.tostring(x, pretty_print=True)) for x in self.root.xpath('//ns:Trackpoint', namespaces={'ns': namespace})]
		points = []
		for lap in self.activity.Lap:
			#~ print lap.values()[0]
			#~ print type(lap)
			tracks =  lap.xpath("*[local-name() = 'Track']")
			#~ print tracks
			for track in tracks:
				for trackpoint in track.xpath("*[local-name() = 'Trackpoint']"):
					
					#~ print trackpoint.Time
					#~ print trackpoint.AltitudeMeters
					#~ print trackpoint.DistanceMeters
					positions = trackpoint.xpath("*[local-name() = 'Position']")
					for pos in positions:
						lat = pos.LatitudeDegrees.pyval
						lon = pos.LongitudeDegrees.pyval
					if len(positions) == 0:
						lat = None
						lon = None
					
					if hasattr(trackpoint, 'HeartRateBpm'):
						hr = trackpoint.HeartRateBpm.Value.pyval
					else:
						hr = None
						
					if hasattr(lap, 'AverageHeartRateBpm'):
						AverageHeartRateBpm = lap.AverageHeartRateBpm.Value.pyval
					else:
						AverageHeartRateBpm = None
						
					if hasattr(lap, 'MaximumHeartRateBpm'):
						MaximumHeartRateBpm = lap.MaximumHeartRateBpm.Value.pyval
					else:
						MaximumHeartRateBpm = None
                    
						
					tp = {
						'Activity':self.activity.attrib['Sport'].lower(),
						'ActivityId':self.activity.Id.text,
                        'TotalDistance': self.distance,
                        'TotalDuration': self.duration,
                        'AveragePace': self.paceseconds,
						'LapStart':lap.values()[0],
						'LapTotalSeconds':lap.TotalTimeSeconds.pyval,
						'LapDistanceMeters':lap.DistanceMeters.pyval,
						'LapAverageHeartRateBpm':AverageHeartRateBpm,
						'LapMaximumHeartRateBpm':MaximumHeartRateBpm,
						'LapIntensity':lap.Intensity.text,
						'LapTriggerMethod':lap.TriggerMethod.text,
						'Time':trackpoint.Time.pyval,
						
						#'DistanceMeters':trackpoint.DistanceMeters.pyval,
						'LatitudeDegrees':lat,
						'LongitudeDegrees':lon,
						'HeartRateBpm':hr,
					
					}
					if hasattr(trackpoint, 'DistanceMeters'):
						tp['DistanceMeters'] = trackpoint.DistanceMeters.pyval
					else:
						tp['DistanceMeters'] = None
					if hasattr(trackpoint, 'AltitudeMeters'):
						tp['AltitudeMeters'] = trackpoint.AltitudeMeters.pyval
					else:
						tp['AltitudeMeters'] = None
					points.append(tp)
		return points
	

    
    @property
    def latitude(self):
        return self.activity.Lap.Track.Trackpoint.Position.LatitudeDegrees.pyval

    @property
    def longitude(self):
        return self.activity.Lap.Track.Trackpoint.Position.LongitudeDegrees.pyval

    @property
    def activity_type(self):
        return self.activity.attrib['Sport'].lower()

    @property
    def started_at(self):
        return self.activity.Lap[0].attrib['StartTime'].pyval
        
    @property
    def completed_at(self):
        return self.activity.Lap[-1].Track.Trackpoint[-1].Time.pyval

    @property
    def distance(self):
        return self._distance
    
    def get_distance(self):
        #return self.activity.Lap[-1].Track.Trackpoint[-2].DistanceMeters.pyval
        dist = 0
        for lap in self.activity.Lap:
            dist += lap.DistanceMeters.pyval
        return dist

    @property
    def distance_units(self):
        return 'meters'

    @property
    def duration(self):
        """Returns duration of workout in seconds."""
        return sum(lap.TotalTimeSeconds for lap in self.activity.Lap)

    @property
    def calories(self):
        return sum(lap.Calories for lap in self.activity.Lap)
        
    @property
    def hr_avg(self):
        """Average heart rate of the workout"""
        hr_data = self.hr_values()
        return sum(hr_data)/len(hr_data)
        
    @property
    def hr_max(self):
        """Minimum heart rate of the workout"""
        return max(self.hr_values())
        
    @property
    def hr_min(self):
        """Minimum heart rate of the workout"""
        return min(self.hr_values())
        
    @property
    def pace(self):
        """Average pace (mm:ss/km for the workout"""
        secs_per_km = self.duration/(self.distance/1000)
        return time.strftime('%M:%S', time.gmtime(secs_per_km))
    
    @property
    def paceseconds(self):
        """Average pace (mm:ss/km for the workout"""
        secs_per_km = self.duration/(self.distance/1000)
        return secs_per_km
    
        
if __name__ == '__main__':
	#~ testFile = '/home/simon/Dropbox/Apps/tapiriik/2015-02-21_18-53-17_4_501_run.tcx'
	testFile = '/home/simon/Dropbox/Apps/tapiriik/2015-06-25_17-59-08_4_585_run.tcx'
	#~ testFile = '/home/simon/Dropbox/Apps/tapiriik/2013-07-11_07-11-2013 Karlsruhe, BW, Germany_Cycling.tcx'
	#~ testFile = 'test.tcx'
	t = TCXParser(testFile)  
	#~ print t.activity_type, t.hr_min, t.hr_max, t.distance
	print t.activity_type, t.distance
	print len(t.positions())
	#~ print t.positions()
        
