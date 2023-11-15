
<template>
  <h1>Other Hello World</h1>
  <div v-if="playlists">
    <table>
      <thead>
      <tr>
        <th>
          Playlist Name
        </th>
        <th>Id</th>
        <th>Export</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="row in playlists.items">
        <td><span>{{row.name}}</span></td>
        <td><span>{{row.id}}</span></td>
        <td><button @click="downloadJson">Download JSON</button></td>
        <!--<td v-for="tableData in row">
          <a v-if="tableData === row['org_name']" :href="'/organization/' + encodeURIComponent(tableData)">{{tableData}}</a>
          <span v-if="tableData !== row['org_name']">{{tableData}}</span>
        </td>-->
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: "Spotify",
  methods: {
    async fetchPlaylists() {
      this.playlists = //(await axios.get("http://localhost:8080/playlists")).data;
          {
            "href": "https://api.spotify.com/v1/me/shows?offset=0&limit=20",
            "limit": 20,
            "next": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
            "offset": 0,
            "previous": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
            "total": 4,
            "items": [
              {
                "collaborative": false,
                "description": "string",
                "external_urls": {
                  "spotify": "string"
                },
                "href": "string",
                "id": "string",
                "images": [
                  {
                    "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
                    "height": 300,
                    "width": 300
                  }
                ],
                "name": "string",
                "owner": {
                  "external_urls": {
                    "spotify": "string"
                  },
                  "followers": {
                    "href": "string",
                    "total": 0
                  },
                  "href": "string",
                  "id": "string",
                  "type": "user",
                  "uri": "string",
                  "display_name": "string"
                },
                "public": false,
                "snapshot_id": "string",
                "tracks": {
                  "href": "string",
                  "total": 0
                },
                "type": "string",
                "uri": "string"
              }
            ]
          };
    },
    async downloadJson() {
      try {
        // Make an Axios request to fetch JSON data
        //const response = await axios.get('https://example.com/api/data'); // Replace with your API endpoint

        // Get the JSON data from the response
        const jsonData = //response.data;
            {
              "collaborative": false,
              "description": "string",
              "external_urls": {
                "spotify": "string"
              },
              "followers": {
                "href": "string",
                "total": 0
              },
              "href": "string",
              "id": "string",
              "images": [
                {
                  "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
                  "height": 300,
                  "width": 300
                }
              ],
              "name": "string",
              "owner": {
                "external_urls": {
                  "spotify": "string"
                },
                "followers": {
                  "href": "string",
                  "total": 0
                },
                "href": "string",
                "id": "string",
                "type": "user",
                "uri": "string",
                "display_name": "string"
              },
              "public": false,
              "snapshot_id": "string",
              "tracks": {
                "href": "https://api.spotify.com/v1/me/shows?offset=0&limit=20",
                "limit": 20,
                "next": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
                "offset": 0,
                "previous": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
                "total": 4,
                "items": [
                  {
                    "added_at": "string",
                    "added_by": {
                      "external_urls": {
                        "spotify": "string"
                      },
                      "followers": {
                        "href": "string",
                        "total": 0
                      },
                      "href": "string",
                      "id": "string",
                      "type": "user",
                      "uri": "string"
                    },
                    "is_local": false,
                    "track": {
                      "album": {
                        "album_type": "compilation",
                        "total_tracks": 9,
                        "available_markets": [
                          "CA",
                          "BR",
                          "IT"
                        ],
                        "external_urls": {
                          "spotify": "string"
                        },
                        "href": "string",
                        "id": "2up3OPMp9Tb4dAKM2erWXQ",
                        "images": [
                          {
                            "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
                            "height": 300,
                            "width": 300
                          }
                        ],
                        "name": "string",
                        "release_date": "1981-12",
                        "release_date_precision": "year",
                        "restrictions": {
                          "reason": "market"
                        },
                        "type": "album",
                        "uri": "spotify:album:2up3OPMp9Tb4dAKM2erWXQ",
                        "artists": [
                          {
                            "external_urls": {
                              "spotify": "string"
                            },
                            "href": "string",
                            "id": "string",
                            "name": "string",
                            "type": "artist",
                            "uri": "string"
                          }
                        ]
                      },
                      "artists": [
                        {
                          "external_urls": {
                            "spotify": "string"
                          },
                          "followers": {
                            "href": "string",
                            "total": 0
                          },
                          "genres": [
                            "Prog rock",
                            "Grunge"
                          ],
                          "href": "string",
                          "id": "string",
                          "images": [
                            {
                              "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
                              "height": 300,
                              "width": 300
                            }
                          ],
                          "name": "string",
                          "popularity": 0,
                          "type": "artist",
                          "uri": "string"
                        }
                      ],
                      "available_markets": [
                        "string"
                      ],
                      "disc_number": 0,
                      "duration_ms": 0,
                      "explicit": false,
                      "external_ids": {
                        "isrc": "string",
                        "ean": "string",
                        "upc": "string"
                      },
                      "external_urls": {
                        "spotify": "string"
                      },
                      "href": "string",
                      "id": "string",
                      "is_playable": false,
                      "linked_from": {},
                      "restrictions": {
                        "reason": "string"
                      },
                      "name": "string",
                      "popularity": 0,
                      "preview_url": "string",
                      "track_number": 0,
                      "type": "track",
                      "uri": "string",
                      "is_local": false
                    }
                  }
                ]
              },
              "type": "string",
              "uri": "string"
            };

        // Convert JSON to a string
        const jsonString = JSON.stringify(jsonData, null, 2);

        // Create a Blob with the JSON string
        const blob = new Blob([jsonString], { type: 'application/json' });

        // Create a link element
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);

        // Set the download attribute with the desired file name
        link.download = 'data.json';

        // Append the link to the document
        document.body.appendChild(link);

        // Trigger a click on the link to start the download
        link.click();

        // Remove the link from the document
        document.body.removeChild(link);
      } catch (error) {
        console.error('Error fetching JSON data:', error);
      }
    },
  },
  data() {
    return {
      apiKey: "some api key",
      playlists: null
    }
  },
  mounted() {
    this.fetchPlaylists();
  }
}
</script>

<style>

</style>
