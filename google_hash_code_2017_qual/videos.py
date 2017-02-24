numbers = lambda st: list(map(int, st.split()))


class Video:
    def __init__(self, id, size):
        self.id = id
        self.size = size
        self.requests = {}
        self.tot_requests = 0

    def __str__(self):
        return 'Video[{}]: {} MB and {} requests({} tot)'.format(self.id,
            self.size, len(self.requests), self.tot_requests)

class Server:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
        self.space_ocupied = 0
        self.e_points = {}
        self.lat_rate = 0
        self.requests = {}
        self.req_list = []

    def act_lat_rate(self):
        """latency rate = (total server rate)/(number of server end points)"""
        tot_lat = sum(self.e_points.values())
        self.lat_rate = tot_lat/len(self.e_points)

    def act_reqs(self, datacenter):
        """actualize all the requests for each video"""
        for video in datacenter.videos:
            for ep, n in video.requests.items():
                if ep in self.e_points.keys():
                    self.requests[video.id] = self.requests.get(ep, 0) + n

    def act_req_list(self, dc):
        """a list version of requests sorted by number of requests"""
        for k, i in self.requests.items():
            self.req_list.append((k, i))

        self.req_list = sorted(self.req_list, key=lambda r: r[1], reverse=True)


    def __str__(self):
        return 'Server[{}]: {} MB and {} Endpoints'.format(self.id,
            self.capacity, len(self.e_points))


class Endpoint:
    def __init__(self, id, lat):
        self.id = id
        self.lat = lat

    def __str__(self):
        return 'Endpoint[{}]: {} latency'.format(self.id, self.lat)

class DataCenter:
    def __init__(self, servers, videos, e_points):
        self.servers = servers
        self.videos = videos
        self.e_points = e_points
        self.solution = {}

    def act_tot_requests(self):
        """complete the variable tot_requests of all the videos"""
        for video in self.videos:
            video.tot_requests = sum(video.requests.values())

    def __str__(self):
        return 'DataCenter: {} servers, {} videos, {} Endpoints'.format(
            len(self.servers), len(self.videos), len(self.e_points))

def act_lat_rates(dc):
    """sort the servers by latency rate"""
    for server in dc.servers:
        server.act_lat_rate()
    
    dc.servers = sorted(dc.servers, key=lambda s: s.lat_rate)

def get_result(dc):
    """add the videos to the cache servers"""
    dc.act_tot_requests()
    act_lat_rates(dc)

    n_servers = len(dc.servers)

    for progress in range(len(dc.servers)):
        server = dc.servers[0]          # lowest lat_rate server

        # Ignore, this just prints the actual progress of the program
        if not (progress+1)%(n_servers/10):
            print('Progress:', str(int((progress+1)*100/n_servers))+'%',
                  end='\r')

        # Compute videos request
        server.act_reqs(dc)
        server.act_req_list(dc)

        # Each element in req_list is a tuple (video id, number of requests)
        for v, r in server.req_list:
            video = dc.videos[v]

            # If possible to add the video to the actual cache server
            if server.space_ocupied+video.size <= server.capacity:
                if not server.id in dc.solution:
                    dc.solution[server.id] = [video.id]
                else:
                    dc.solution[server.id].append(video.id)

                server.space_ocupied += video.size

                # Delete requests from end points for the video added
                for ep in server.e_points.keys():
                    if ep in video.requests:
                        video.requests[ep] = 0

        dc.servers.pop(0)
        act_lat_rates(dc)

    # Transform solution into list, not necesary but I did for convenience
    final_sol = []
    for k, v in dc.solution.items():
        temp = [k, v]
        final_sol.append(temp)

    return final_sol

def read_in_file(filename):
    """read input file and process the data"""
    with open(filename, 'r') as fn:
        get = lambda func: func(fn.readline())

        n_videos, n_e_points, r_decrps, n_servers, cap = get(numbers)
        sizes = get(numbers)

        # List of all the cache servers
        servers = []
        for id in range(n_servers):
            servers.append(Server(id, cap))

        # List of all the videos
        videos = []
        for id, size in enumerate(sizes):
            videos.append(Video(id, size))

        # List of all the end points
        e_points = []
        for id in range(n_e_points):
            lat, n_servers_c = get(numbers)
            e_points.append(Endpoint(id, lat))
            
            # Complete end points of all servers
            for __ in range(n_servers_c):
                s_id, s_lat = get(numbers)
                servers[s_id].e_points[id] = s_lat

        # Complete the requests from the end points for each video
        for r in range(r_decrps):
            video, ep, n = get(numbers)
            videos[video].requests[ep] = n

    return DataCenter(servers, videos, e_points)        


def write_solution(filename, result):
    """write the soulution to the output file"""
    with open(filename, 'w') as fn:
        fn.write('%d\n' % len(result))

        for r in result:
            fn.write(str(r[0])+' ' + ' '.join([str(x) for x in r[1]]) + '\n')


if __name__ == '__main__':

    # THE INPUT FILES MUST BE IN THE SAME FOLDER AS video.py
    kittens = 'kittens.in'
    matz = 'me_at_the_zoo.in'
    tt = 'trending_today.in'
    vws = 'videos_worth_spreading.in'
    in_files = [vws, matz, tt, kittens]

    for in_file in in_files:
        out_file = in_file + '.out'

        datacenter = read_in_file(in_file)

        print(datacenter)
        # print(datacenter.servers[0])
        # print(datacenter.e_points[0])
        # print(datacenter.videos[0])
        # print(datacenter.videos[0].requests)

        try:
            result = get_result(datacenter)
        except KeyboardInterrupt:
            pass

        write_solution(out_file, result)
        
