package org.libreoffice.example.clipboardapi;

import java.net.MalformedURLException;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.LinkedList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;;

public class ClipboardServer {
	
	private RequestHandler rqHandler;
	private List<ClipEntry> cachedEntries;

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
	
	private ClipEntry fillEntry(JSONObject c) {
		ClipEntry toReturn = new ClipEntry(c);
		toReturn.setMimetype((String) c.get("mimetype"));
		toReturn.setData((String) c.get("data"));
		
		return toReturn;
	}
	
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
	
	public Collection<ClipEntry> getCachedClips() {
		return cachedEntries;
	}
}
