package org.libreoffice.example.clipboardapi;

import java.net.MalformedURLException;
import java.util.Collection;
import java.util.List;
import java.util.LinkedHashMap;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;;

public class ClipboardServer {
	
	private RequestHandler rqHandler;

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
		ClipEntry<String> toReturn = new ClipEntry<String>(c);
		toReturn.setMimetype((String) c.get("mimetype"));
		toReturn.setData((String) c.get("data"));
		
		return toReturn;
	}
	
	public Collection<ClipEntry> getAllClips() {
		JSONArray rawClips = rqHandler.getAllClips();
		LinkedHashMap<String, ClipEntry> clips = new LinkedHashMap<String, ClipEntry>(200, 0.75f);
		for (int i = 0; i < rawClips.size(); i++) {
			JSONObject c = (JSONObject) rawClips.get(i);
			ClipEntry<String> ce = fillEntry(c);
			String parentId = (String) c.get("parent");
			if ( parentId != null) {
				System.out.println("insertign child");
				clips.get(parentId).addChild(ce);
				System.out.println("done inserting child");
			}
			else {
				System.out.println("inserting parent");
				clips.put(ce.getId().toString(), ce);
			}
		}
		System.out.println("before returning");
		return (clips.values());
	}
}
