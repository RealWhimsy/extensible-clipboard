package org.libreoffice.example.clipboardapi;

import java.util.Base64;
import java.util.Base64.Decoder;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;
import java.util.UUID;

import org.json.simple.JSONObject;

public class ClipEntry {

	private UUID _id;
	private Date creationDate;
	private String mimetype;
	private String data;
	private byte[] bin_data;
	private String filename;
	private List<ClipEntry> children = new LinkedList<ClipEntry>();
	private Decoder b64decoder; 
	
	public ClipEntry(String uuid) {
		_id = UUID.fromString(uuid);
		b64decoder = Base64.getDecoder();
	}
	
	public ClipEntry(JSONObject json) {
		_id = UUID.fromString( ((String) json.get("_id")) );
		b64decoder = Base64.getDecoder();
	}
	
	public Date getCreationDate() {
		return creationDate;
	}

	public void setCreationDate(Date creationDate) {
		this.creationDate = creationDate;
	}

	public String getFilename() {
		return filename;
	}

	public void setFilename(String filename) {
		this.filename = filename;
	}

	public UUID getId() {
		return _id;
	}
	
	public String getMimetype() {
		return mimetype;
	}
	
	public void setMimetype(String mimetype) {
		this.mimetype = mimetype;
	}
	
	public String getData() {
		return data;
	}
	
	public byte[] getBinData() {
		return bin_data;
	}
	
	/**
	 * Sets the data of the object.
	 * This method will automatically deterimine if the content of data are
	 * a base64-encoded binary object or just a String and set it to either
	 * data or binData as needed
	 * @param data Data for this object
	 */
	public void setData(String data) {
		try {
			bin_data = b64decoder.decode(data);
		} catch (IllegalArgumentException e) {
			this.data = data;
		}
	}
	
	public List<ClipEntry> getChildren() {
		return children;
	}
	
	public void addChild(ClipEntry child) {
		children.add(child);
	}
	
}
