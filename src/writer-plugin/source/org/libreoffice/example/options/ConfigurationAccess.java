/*
 *  OptionsPageDemo - OpenOffice.org Demo Extension
 *  "How to access and update configuration data of an extension"
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 *  You can use this code in your application without any restrictions.
 */

package org.libreoffice.example.options;

import org.libreoffice.example.helper.DialogHelper;

import com.sun.star.awt.XControl;
import com.sun.star.awt.XControlContainer;
import com.sun.star.awt.XWindow;
import com.sun.star.beans.PropertyState;
import com.sun.star.beans.PropertyValue;
import com.sun.star.beans.XPropertySet;
import com.sun.star.container.XNameAccess;
import com.sun.star.lang.XMultiServiceFactory;
import com.sun.star.uno.UnoRuntime;
import com.sun.star.uno.XComponentContext;

/**
 * Provides generic factory methods around configuration access.
 * 
 * @author Christian Lins (christian.lins@sun.com)
 */
public class ConfigurationAccess {
	/**
	 * Creates a XNameAccess instance for read and write access to the configuration
	 * at the given node path.
	 * 
	 * @param context
	 * @param path
	 * @return
	 */
	public static XNameAccess createUpdateAccess(XComponentContext context, String path) {
		XNameAccess access;

		// Create the com.sun.star.configuration.ConfigurationUpdateAccess
		// for the registry node which contains the data for our option
		// pages.
		XMultiServiceFactory xConfig;

		try {
			xConfig = (XMultiServiceFactory) UnoRuntime.queryInterface(XMultiServiceFactory.class,
					context.getServiceManager()
							.createInstanceWithContext("com.sun.star.configuration.ConfigurationProvider", context));
		} catch (com.sun.star.uno.Exception e) {
			e.printStackTrace();
			return null;
		}

		// One argument for creating the ConfigurationUpdateAccess is the "nodepath".
		// Our nodepath point to the node of which the direct subnodes represent the
		// different options pages.
		Object[] args = new Object[1];
		args[0] = new PropertyValue("nodepath", 0, path, PropertyState.DIRECT_VALUE);

		// We get the com.sun.star.container.XNameAccess from the instance of
		// ConfigurationUpdateAccess and save it for later use.
		try {
			access = (XNameAccess) UnoRuntime.queryInterface(XNameAccess.class,
					xConfig.createInstanceWithArguments("com.sun.star.configuration.ConfigurationUpdateAccess", args));
		} catch (com.sun.star.uno.Exception e) {
			e.printStackTrace();
			return null;
		}

		return access;
	}

	public static String getServerUrl(XNameAccess accessLeaves) throws com.sun.star.uno.Exception {
		// This is an implementation which will be used for several options pages
		// which all have the same controls. m_arStringControls is an array which
		// contains the names.
		// load the values from the registry
		// To access the registry we have previously created a service instance
		// of com.sun.star.configuration.ConfigurationUpdateAccess which supports
		// com.sun.star.container.XNameAccess. We obtain now the section
		// of the registry which is assigned to this options page.
		XPropertySet xLeaf = (XPropertySet) UnoRuntime.queryInterface(XPropertySet.class,
				accessLeaves.getByName("FooOptionsPage"));
		if (xLeaf == null)
			throw new com.sun.star.uno.Exception("XPropertySet not supported.");

		// The properties in the registry have the same name as the respective
		// controls. We use the names now to obtain the property values.
		Object aValue = xLeaf.getPropertyValue("txtUrl");
		return aValue.toString();
	}
}
