package org.libreoffice.example.clipboardapi;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.IOException;
import java.lang.String;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

/**
 * This class is responsible for the communication to the server on a lower
 * level. Retrieved data will be passed into JSON-objects
 */
public class RequestHandler {
	
	/** Used to parse received clips into JSON */
	private JSONParser parser;
	/** Root Url of the server */
	private URL serverUrl;
	/** Url under which clips can be saved or retrieved. serverUrl/clip/ by default */
	private URL clipUrl;
	
	/**
	 * Construcs a new instance
	 * @param baseUrl Base url of the Clipboard server
	 * @throws MalformedURLException If baseUrl is not correct according to java.net.URL
	 */
	public RequestHandler(String baseUrl) throws MalformedURLException {
		updateServerUrl(baseUrl);
		parser = new JSONParser();
	}
	
	/**
	 * Sets the currently used serverUrl
	 * @param baseUrl String representing the Url to be used
	 * @throws MalformedURLException If baseUrl is not correct according to java.net.URL
	 */
	public void updateServerUrl(String baseUrl) throws MalformedURLException {
		serverUrl = new URL(baseUrl);
		clipUrl = new URL(baseUrl.concat("clip/"));
	}
	
	/**
	 * Makes an HTTP-Request and parses the response to a String
	 * @param conn Preconfigured HttpURLConnection that will be executed.
	 *   No further actions will be made so be sure that everything is set correctly
	 * @return A String containing the data from the response
	 * @throws IOException If the connection failed
	 */
	private String buildStringFromConnection(HttpURLConnection conn) throws IOException{
		InputStream in = conn.getInputStream();
		BufferedReader br = new BufferedReader( new InputStreamReader(in) );
		StringBuilder response = new StringBuilder();
		String line;
		line = br.readLine();
		while ( line != null ) {
			response.append(line);
			response.append("\n");
			line = br.readLine();
		}
		br.close();
		return response.toString();

	}

	/**
	 * This method will make a connection to the server specified in serverUrl and
	 * request all available clips. It then proceeds to retrieve the data for all clips.
	 * @return All received clips parsed to JSON, sorted ascending by creation_date.
	 *   The keys correspond to the ones used on the server, important ones:
	 *   _id, data, creation_date
	 */
	public JSONArray getAllClips() {
		JSONArray json = new JSONArray();
		try {
			HttpURLConnection conn = (HttpURLConnection) clipUrl.openConnection();
			conn.setRequestProperty("Contenty-Type", "application/json");
			conn.setInstanceFollowRedirects(true);
			conn.setConnectTimeout(3000);
			
			String result = buildStringFromConnection(conn);
			json = (JSONArray) parser.parse(result);
			
			for (int i = 0; i < json.size(); i++) {
				JSONObject curr = (JSONObject) json.get(i);
				byte[] data = getClipData(curr.get("_id").toString());
				if (curr.get("mimetype").toString().contains("text/")) {
					curr.put("data", new String(data));
				}
				else {
					curr.put("data", data);
				}
			}
			
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ParseException e) {
			e.printStackTrace();
		}
		return json;
	}
	
	/**
	 Makes an HTTP-Request and parses the response to a byte[].
	 This will be used if the clip is not a string but binary data, eg. an image
	 * @param conn Preconfigured HttpURLConnection that will be executed.
	 *   No further actions will be made so be sure that everything is set correctly
	 * @return A byte[] containing the data from the response or null if the connection failed.
	 */
	private byte[] getDataFromConnection(HttpURLConnection conn) {
		byte[] result = null;
		InputStream in;
		try {
			in = conn.getInputStream();
			return in.readAllBytes();
		} catch (IOException e) {
			return null;
		}

	}
	
	/**
	 * Requests the server to get a specific cilp
	 * @param id _id of the clip to be requested, needs to be a UUID4- compatible string
	 * @return A byte[] containg the binary data gotten from the server.
	 *  According to the mimetype, this may either be a UTF-8-encoded String or
	 *  simply binary data
	 */
	public byte[] getClipData(String id) {
		try {
			URL objectUrl = new URL(clipUrl + id + "/");
			HttpURLConnection conn = (HttpURLConnection) objectUrl.openConnection();
			conn.setInstanceFollowRedirects(true);
			conn.setConnectTimeout(3000);
			return getDataFromConnection(conn);			
		} catch (IOException e) {
			return null;
		}
	}
	
	/**
	 * POSTs data the server.
	 * @param toSend JSONObject containing a String as data
	 * @return true, if server created a new object and responded with 201
	 *  	   false, otherwise
	 */
	public boolean sendStringToServer(JSONObject toSend) {
		try {
			HttpURLConnection conn = (HttpURLConnection) clipUrl.openConnection();
			conn.setRequestMethod("POST");
			conn.setRequestProperty("Contenty-Type", "text/plain");
			conn.setInstanceFollowRedirects(true);
			conn.setConnectTimeout(3000);
			
			OutputStreamWriter wr= new OutputStreamWriter(conn.getOutputStream());
			wr.write(toSend.toString());
			wr.close();
			
			if (conn.getResponseCode() == 201) {
				return true;
			}
			
		} catch (Exception e) {
			return false;
		}
		return false; // no 201
	}
}
