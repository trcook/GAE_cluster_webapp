# Webapp for cluster computing

This project is a side-product of the [rdocker_hpc](https://github.com/trcook/rdockerhpc) project. It aims to provide a usable web interface to end-users in a Research environment. Deployment is not fully automated and special care will be needed to create routing rules etc for these services to work.

* Note: This webapp is designed for use with google's computing platform (GCE) and specifically, for deployment on google's appengine.


# Key technologies/Files:

 * Flask as the driver for the webapp
 * Custom Rstudio server images (see the 'debian_rstudio_server_config.sh'.
 you can use this to setup a debian (Jesse))
     * Rstudio server is the accesspiont for end-users to run their analyses in R. The setup here is just as ammenible to setting up a Ipython notebook server for end-users to access and run python scripts.

        
# THIS IS NOT READY FOR DEPLOYMENT. 
You can check back here soon. I have dev versions of this running and internal-facing versions of this running at OEF, but the files posted here are not entirely ready for deployment.  The dockerized version of the rstudio image in particular is not prepared and I have not yet built an interface for data into the kubernetes setup in the kube-setup directory. Nor have I built out the interface for launching the cluster -- though this is really quite simple on GCS -- it's just a matter of programming in the api calls.
