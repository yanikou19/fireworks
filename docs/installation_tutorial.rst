==========================================
Installation Tutorial (part 1: the Server)
==========================================

This tutorial will guide you through FireWorks installation on the central server. The purpose of this tutorial is to get you set up as quickly as possible; it isn't intended to demonstrate the features of FireWorks or explain things in great detail.

This tutorial can be safely completed from the command line, and requires no programming.

Set up the central server (FireServer)
======================================

The FireWorks central server (FireServer) hosts the FireWorks database. For production, you should choose a central server that has a fixed IP address/hostname so that you can connect to it from other machines reliably. For initially testing the installation, it should be OK to use a laptop or workstation with a dynamic IP. To set up a FireServer:

1. Follow the instructions listed at :doc:`Basic FireWorks Installation </installation>`.

2. Install `MongoDB <http://www.mongodb.org>`_ on the server.

3. Start MongoDB::

    mongod &

You are now ready to start playing with FireWorks!

.. note:: If MongoDB is outputting a lot of text, you might want to start it in a dedicated Terminal window or use the ``--quiet`` option. In addition, if you are running it on a shared machine, make sure that the ``--dbpath`` variable is set to a directory that you can access.

Reset the FireServer
--------------------

1. Navigate to the FireWorks installation tutorial directory::

    cd <INSTALL_DIR>/fw_tutorials/installation

where <INSTALL_DIR> is your FireWorks installation directory.
 
2. Reset the FireWorks database (the LaunchPad)::

    lp_run.py reset <TODAY'S DATE>

where <TODAY'S DATE> is formatted like '2012-01-31' (this serves as a safeguard to accidentally overwriting an existing database). You should receive confirmation that the LaunchPad was reset.

.. note:: If you are already curious about the various options that the LaunchPad offers, you can type ``lp_run.py -h``. The ``-h`` help option is available for all of the scripts in these tutorials.

Add a FireWork to the FireServer database
-----------------------------------------

A FireWork contains the computing job to be performed. For this tutorial, we will use a FireWork that consists of only a single step. We'll tackle more complex workflows in other tutorials.

1. Staying in the tutorial directory, run the following command::

    lp_run.py add fw_test.yaml

   .. note:: You can look inside the file ``fw_test.yaml`` with a text editor if you'd like; we'll explain its components shortly.

2. You should have received confirmation that the FireWork got added. You can query the database for this FireWork as follows::

    lp_run.py get_fw 1

This prints out the FireWork with ``fw_id`` = 1 (the first FireWork entered into the database)::

    {
        "created_on": "2013-01-31T05:10:27.911000",
        "fw_id": 1,
        "spec": {
            "_tasks": [
                {
                    "_fw_name": "Script Task",
                    "parameters": {
                        "use_shell": true,
                        "script": "echo \"howdy, your job launched successfully!\" >> howdy.txt"
                    }
                }
            ]
        },
        "state": "READY"
    }


3. Some of the FireWork is straightforward, but a few sections deserve further explanation:

* The **spec** of the FireWork contains *all* the information about what job to run and the parameters needed to run it.
* Within the **spec**, the **_tasks** section tells you what jobs will run. The ``Script Task`` is a particular type of task that runs commands through the shell. Other sections of the **spec** can be also be defined, but for now we'll stick to just **_tasks**.
* This FireWork runs the command ``echo "howdy, your job launched successfully!" >> howdy.txt"``, which prints text to a file named ``howdy.txt``.
* The **state** of *READY* means the FireWork is ready to be run.

You have now stored a FireWork in the LaunchPad, and it's ready to run!

.. note:: More details on using the ``ScriptTask`` are presented in the later tutorials.

Launch a Rocket on the FireServer
=================================

A Rocket fetches a FireWork from the LaunchPad and runs it. A Rocket might be run on a separate machine (FireWorker) or through a queuing system. For now, we will run the Rocket on the FireServer itself and without a queue.

1. Navigate to any clean directory. For example::

    mkdir ~/fw_tests
    cd ~/fw_tests
    
2. We can launch Rockets using the Rocket Launcher. Execute the following command (once)::

    rlauncher_run.py singleshot
    
The Rocket fetches an available FireWork from the FireServer and runs it.

3. Verify that the desired task ran::

    cat howdy.txt
    
You should see the text: ``howdy, your job launched successfully!``

.. note:: In addition to ``howdy.txt``, you should also see a file called ``fw.json``. This contains a JSON representation of the FireWork that the Rocket ran and can be useful later for tracking down a launch or debugging.

4. Check the status of your FireWork::

    lp_run.py get_fw 1
    
You will now see lots of information about your Rocket launch, such as the time and directory of the launch. You should also notice that the state of the FireWork is now ``COMPLETED``.

5. Try launching another rocket (you should get an error)::   

    rlauncher_run.py singleshot

The error ``No FireWorks are ready to run and match query!`` indicates that the Rocket tried to fetch a FireWork from the database, but none could be found. Indeed, we had previously run the only FireWork that was in the database.

Launch many Rockets (rapidfire mode)
====================================

If you just want to run many jobs on the central server itself, the simplest way is to run the Rocket Launcher in "rapidfire mode". Let's try this feature:

1. Staying in your working directory from last time, clean up your output files::

    rm fw.json howdy.txt

#. Let's add 3 identical FireWorks::

    cp <INSTALL_DIR>/fw_tutorials/installation/fw_test.yaml .
    lp_run.py add fw_test.yaml
    lp_run.py add fw_test.yaml
    lp_run.py add fw_test.yaml

#. Confirm that the three FireWorks got added to the database, in addition to the one from before (4 total)::

    lp_run.py get_fw_ids

#. We could also just get the ``fw_id`` of jobs that are ready to run (our 3 new FireWorks)::

    lp_run.py get_fw_ids -q '{"state":"READY"}'

#. Let's run launch Rockets in "rapidfire" mode, which will keep repeating until we run out of FireWorks to run::

    rlauncher_run.py rapidfire

#. You should see three directories starting with the tag ``launcher_``. Inside each of these directories, you'll find the results of one of your FireWorks (a file named ``howdy.txt``).


Running FireWorks automatically
===============================

We can set our Rocket Launcher to continuously look for new FireWorks to run. Let's try this feature.

1. Staying in your working directory from last time, clean up your previous output files::

    rm -r launcher_*

#. Start the Rocket Launcher so that it looks for new FireWorks every 10 seconds::

    rlauncher_run.py rapidfire --nlaunches infinite --sleep 10

#. **In a new terminal window**, navigate back to your working directory containing ``fw_test.yaml``. Let's insert two FireWorks::

    lp_run.py add fw_test.yaml
    lp_run.py add fw_test.yaml

#. After a few seconds, the Rocket Launcher should have picked up the new jobs and run them. Confirm this is the case::

    ls -d launcher_*

   You should see two directories, one for each FireWork we inserted.

#. You can continue adding FireWorks as desired; the Rocket Launcher will run them automatically and create a new directory for each job. When you are finished, you can exit out of the Rocket Launcher terminal window and delete your working directory.

#. As with all FireWorks scripts, you can run the built-in help for more information::

    rlauncher_run.py -h
    rlauncher_run.py singleshot -h
    rlauncher_run.py rapidfire -h

What just happened?
===================

It's important to understand that when you add a FireWork to the LaunchPad, the job just sits in the database and waits. The LaunchPad does not submit jobs to a computing resource when a new FireWork is added to the LaunchPad. Rather, a computing resource must *request* a computing task by running the Rocket Launcher.

When we ran the Rocket Launcher in rapid-fire mode, the Rocket Launcher requests a new task from the LaunchPad immediately after completing its current task. It stops requesting tasks when none are left in the database. It might *seem* like the LaunchPad is the one in charge, but in reality the Rocket Launcher must initiate the request for a FireWork. You might have noticed this when we ran the Rocket Launcher in infinite mode with a sleep time of 10. In this mode, we are requesting a new task every 10 seconds after completing the previous task. When you add a new FireWork to the LaunchPad, it does not start running automatically. We must wait for the Rocket Launcher to request it!


Next steps
==========

At this point, you've successfully stored a simple job in a database and run it later on command. You even executed multiple jobs with a single command: ``rlauncher_run.py rapidfire``, and run jobs automatically using the **infinite** Rocket Launcher. This should give a basic feeling of how you can automate many jobs using FireWorks.

Your next step depends on your application. If you want to stick with our simple script and automate it on at least one worker node, forge on to the next tutorial in the series: :doc:`Installation Tutorial (part 2: the Worker) </installation_tutorial_pt2>`. This is the path we recommend for most users, except in the simplest of circumstances in which you only want to run jobs on the FireServer itself.

If you are only running on the FireServer, you can skip ahead to :doc:`defining jobs using FireTasks </firetask_tutorial>`.