package org.libreoffice.example.dialog;

import java.util.Collection;
import java.util.List;

import org.libreoffice.example.clipboardapi.ClipboardServer;
import org.libreoffice.example.clipboardapi.ClipEntry;
import org.libreoffice.example.helper.DialogHelper;

import com.sun.star.awt.XControl;
import com.sun.star.awt.XControlModel;
import com.sun.star.awt.tree.XMutableTreeDataModel;
import com.sun.star.awt.tree.XMutableTreeNode;
import com.sun.star.awt.tree.XTreeControl;
import com.sun.star.awt.tree.XTreeNode;
import com.sun.star.awt.XDialog;
import com.sun.star.awt.XDialogEventHandler;
import com.sun.star.beans.XPropertySet;
import com.sun.star.lang.WrappedTargetException;
import com.sun.star.uno.Any;
import com.sun.star.uno.Type;
import com.sun.star.uno.Exception;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;
import com.sun.star.view.XSelectionSupplier;

/**
 * This class represents the tree of clips visible on the ClipSelectDialog
 */
public class ClipTreeDialog implements XDialogEventHandler {

	private XComponentContext xContext;
	private XDialog dialog;
	private static final String actionOk = "actionOk";
	private static final String actionInsert = "actionInsert";
	private static final String actionSync = "actionSync";
	private String[] supportedActions = new String[] { actionOk, actionSync };
	private ClipboardServer cbServer;
	private Collection<ClipEntry> currentItems;

	public ClipTreeDialog(XComponentContext xContext, ClipboardServer cbServer) throws Exception {
		this.xContext = xContext;
		this.cbServer = cbServer;
		this.dialog = DialogHelper.createDialog("ClipSelectDialog.xdl", this.xContext, this);
		initCachedTree();
	}
	
	/**
	 * Tries to fill the tree with previously cached items from ClipboardServer
	 */
	private void initCachedTree() throws Exception{
		currentItems = cbServer.getCachedClips();
		fillTree();
	}

	/**
	 * Builds the visible representation of the Tree itself
	 */
	public void fillTree() throws Exception {
		if ( currentItems == null ) {
			return;
		}
		// https://forum.openoffice.org/en/forum/viewtopic.php?f=20&t=7348
		XControl tree = DialogHelper.getTree(this.dialog, "ClipTree");
		XControlModel model = tree.getModel();

		Object xTreeData = this.xContext.getServiceManager()
				.createInstanceWithContext("com.sun.star.awt.tree.MutableTreeDataModel", this.xContext);
		XMutableTreeDataModel mxTreeDataModel = (XMutableTreeDataModel) UnoRuntime
				.queryInterface(XMutableTreeDataModel.class, xTreeData);
		Type type = new Type(java.lang.String.class);
		Any any = new Any(type, "Root");
		XMutableTreeNode root = mxTreeDataModel.createNode(any, true);
		for (ClipEntry c : currentItems) {
			any = new Any(type, c.getCreationDate() + " | " + c.getMimetype());
			XMutableTreeNode parent = mxTreeDataModel.createNode(any, true);
			root.appendChild(parent);
			List<ClipEntry> children = c.getChildren();
			for (ClipEntry child : children) {
				any = new Any(type, child.getCreationDate() + " | " + child.getMimetype());
				XMutableTreeNode childNode = mxTreeDataModel.createNode(any, true);
				parent.appendChild(childNode);
			}
		}

		mxTreeDataModel.setRoot(root);
		XPropertySet xTreeModelProperty = (XPropertySet) UnoRuntime.queryInterface(XPropertySet.class, model);
		xTreeModelProperty.setPropertyValue("DataModel", mxTreeDataModel);
	}

	public void show() {
		dialog.execute();
	}

	/**
	 * Closes the Dialog. 
	 * The button itself is not present anymore
	 */
	private void onOkButtonPressed() {
		dialog.endExecute();
	}

	/**
	 * This will trigger cbServer to get all visible clips from the remote
	 * Clipboard-server
	 */
	private void onSyncButtonPressed() {
		currentItems = cbServer.getClipsFromServer();
		try {
			fillTree();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	/**
	 * Finds the ClipEntry corresponding to the currently selected
	 * node of the tree
	 * @param value Visible value selcted
	 * @return The ClipEntry the user has selected right now.
	 * 	null, if none could be found, should only ever happen when root is selected
	 */
	private ClipEntry findEntry(String value) {
		for (ClipEntry curr : currentItems) {
			if (value.contains(curr.getCreationDate()) && value.contains(curr.getMimetype())) {
				return curr;
			}
			for (ClipEntry child : curr.getChildren()) {
				if (value.contains(child.getCreationDate()) && value.contains(child.getMimetype())) {
					return child;
				}
			}
		}
		return null;
	}
	
	/**
	 * User clicked on insert. Gets the data of the currently selected tree-node 
	 * and inserts it into the current cursor-position
	 */
	private void onInsertPressed() {
		XTreeControl xtreeControl = DialogHelper.getTreeControl(dialog, "ClipTree");
		XSelectionSupplier ss = (XSelectionSupplier) xtreeControl;
		Any selection = (Any) ss.getSelection();
		XTreeNode tn = (XTreeNode) selection.getObject();
		ClipEntry c = findEntry(tn.getDisplayValue().toString());
		DataHelper.insertIntoGUICursor(xContext, c);
		// End dialog
		onOkButtonPressed();
	}

	/**
	 * New buttons need to be registered here
	 */
	@Override
	public boolean callHandlerMethod(XDialog dialog, Object eventObject, String methodName)
			throws WrappedTargetException {
		if (methodName.equals(actionOk)) {
			onOkButtonPressed();
			return true; // Event was handled
		}
		if (methodName.equals(actionInsert)) {
			onInsertPressed();
			return true;
		}
		if (methodName.equals(actionSync)) {
			onSyncButtonPressed();
			return true;
		}
		return false; // Event was not handled
	}

	@Override
	public String[] getSupportedMethodNames() {
		return supportedActions;
	}

}
