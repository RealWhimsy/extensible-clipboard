package org.libreoffice.example.clipboardapi;

import java.net.MalformedURLException;
import java.text.DateFormat;
import java.text.ParseException;
import java.util.Collection;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.LinkedList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;;

public class ClipboardServer {
	/**
	 * This class is responsible for the communication with the server.
	 * Clients should use it to retrieve or save clips
	 */
	
	/** Responsible for lower-level communication */
	private RequestHandler rqHandler;
	/** Will save already retrieved entries to minimize traffic */
	private List<ClipEntry> cachedEntries;

	/**
	 * Sets the URL that will be called in subsequent requests
	 * @param baseUrl A String representing the URL
	 * @return true, if baseUrl was well-formed and can be used for requests
	 * 		   false, if not
	 */
	public boolean setServerURL(String baseUrl) {
		try {
			if ( rqHandler == null) {
				rqHandler = new RequestHandler(baseUrl);
			}
			else {
				rqHandler.updateServerUrl(baseUrl);
			}
			return true;
		} catch (MalformedURLException e) {
			return false;
		}
	}
	
	/**
	 * Takes a JSONObject and build a ClipEntry from it.
	 * Currently saves mimetype, data and creationDate
	 * @param c JSONObject to be parsed
	 * @return The populated ClipEntry
	 */
	private ClipEntry fillEntry(JSONObject c) {
		ClipEntry toReturn = new ClipEntry(c);
		toReturn.setMimetype((String) c.get("mimetype"));
		toReturn.setData(c.get("data"));
		toReturn.setCreationDate((String)c.get("creation_date"));
		return toReturn;
	}
	
	/**
	 * Retrieves all save (or visible) clips from the server including
	 * their metadata.
	 * @return A Collection containing all ClipEntry's and their respective children
	 */
	public Collection<ClipEntry> getClipsFromServer() {
		JSONArray rawClips = rqHandler.getAllClips();
		LinkedHashMap<String, ClipEntry> clips = new LinkedHashMap<String, ClipEntry>(200, 0.75f);
		for (int i = 0; i < rawClips.size(); i++) {
			JSONObject c = (JSONObject) rawClips.get(i);
			ClipEntry ce = fillEntry(c);
			String parentId = (String) c.get("parent");
			if ( parentId != null) {
				clips.get(parentId).addChild(ce);
			}
			else {
				clips.put(ce.getId().toString(), ce);
			}
		}
		cachedEntries = new LinkedList<ClipEntry>(clips.values());
		Collections.reverse(cachedEntries);
		return cachedEntries;
	}
	
	/**
	 * Saves a text/plain object on the server
	 * @param text The String to be saved
	 * @return True, if text was saved successfully
	 * 		   False, otherwise
	 */
	public boolean sendStringToServer(String text) {
		JSONObject toSend = new JSONObject();
		toSend.put("mimetype", "text/plain");
		toSend.put("data", text);
		return rqHandler.sendStringToServer(toSend);
	}
	
	/**
	 * @return a list with all cached entries, may be empty
	 */
	public Collection<ClipEntry> getCachedClips() {
		return cachedEntries;
	}
}
