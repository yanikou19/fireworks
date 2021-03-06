=================================
Dealing with Failures and Crashes
=================================

Job exceptions, node failures, and system outages are all unfortunate realities of executing workflows. You'll likely encounter some of these events when running FireWorks. This tutorial will simulate some of these events, so you can see how FireWorks detects job failures and what you can do about it.

Normal operation
================

Let's first introduce normal operation of a FireWork that prints ``starting``, sleeps for 10 seconds, and then prints ``ending``. The FireWork is completed successfully only if ``ending`` gets printed.

#. Move to the ``failures`` tutorial directory on your FireServer::

    cd <INSTALL_DIR>/fw_tutorials/failures

#. Look inside ``fw_sleep.yaml``. It should be pretty straightforward - we are printing text, sleeping, and printing text again.

   .. note:: You can increase or decrease the sleep time, depending on your patience level and reaction time later on in the tutorial.

#. Let's add and run this FireWork. You'll have to wait 10 seconds for it to complete::

    lp_run.py reset <TODAY'S DATE>
    lp_run.py add fw_sleep.yaml
    rlauncher_run.py singleshot

#. Hopefully, your patience was rewarded with ``ending`` printed to your terminal. If so, let's keep going!

Error during run - a *FIZZLED* Firework!
========================================

If your job throws an exception (error), FireWorks will automatically mark your job as *FIZZLED*. Any jobs that depend on this job will not run until you fix things. Let's simulate this situation.

#. Reset your database and add back the sleeping FireWork::

    lp_run.py reset <TODAY'S DATE>
    lp_run.py add fw_sleep.yaml

#. We'll run the FireWork again, but this time you should interrupt its operation using the keyboard shortcut to stop execution(Ctrl+C or Ctrl+\). Make sure you hit that keyboard combo immediately after running the job, before you see the text ``ending``::

    rlauncher_run.py singleshot
    (Ctrl+C or Ctrl+\)

#. If you did this correctly, you'll have seen the text ``starting`` but not the text ``ending``. You might also see some error text printed to your terminal.

#. This behavior is what happens when your job throws an error (such as the *KeyboardInterrupt* error we just simulated). Let's see what became of this ill-fated FireWork::

    lp_run.py get_fw 1

#. You should notice the state of this FireWork is automatically marked as *FIZZLED*. In addition, if you look at the **stored_data** key, you'll see that there's information about the error that was encountered during the run.

#. If at any point you want to review what FireWorks have *FIZZLED*, you can use the following query::

    lp_run.py get_fw_ids -q '{"state":"FIZZLED"}'

Catastrophic Failure
====================

The previous failure was easy to detect; the job threw an error, and the Rocket was able to catch that error and tell the LaunchPad to mark the job as *FIZZLED*. However, more catastrophic failures are possible. For example, you might have a power failure in your computer center. In that case, there is no time for the Rocket to report to FireWorks that there is a failure. Let's see how to handle this case.

#. Reset your database and add back the sleeping FireWork::

    lp_run.py reset <TODAY'S DATE>
    lp_run.py add fw_sleep.yaml

#. We'll run the FireWork again, but this time you should interrupt its operation by **forcibly closing your terminal window** (immediately after running the job, before you see the text ``ending``)::

    rlauncher_run.py singleshot
    ----(forcibly close your terminal window)

#. Now let's re-open a terminal window and see what FireWorks thinks is happening with this job::

    lp_run.py get_fw 1

#. You should notice that FireWorks still thinks this job is *RUNNING*! We can fix this using the following command::

    lp_run.py detect_fizzled --time 1 --fix

#. This command will mark all jobs that have been running for more than 1 second as *FIZZLED*. We'll improve this in a bit, but for now let's check to make sure the command worked::

    lp_run.py get_fw 1

#. The FireWork should now be correctly listed as *FIZZLED*!

#. Of course, in production you'll never want to mark all jobs running for 1 second as being *FIZZLED*; this will mark jobs that are running properly as *FIZZLED*!

#. In production, you need not specify the ``--time`` parameter at all. FireWorks will automatically detect a job as *FIZZLED* after 4 hours of idle time when you run ``lp_run.py detect_fizzled``. Jobs that are running properly, even if they take longer than 4 hours, will not be marked as *FIZZLED*. This is because the Rocket will automatically ping the LaunchPad that it's *alive* every hour. FireWorks will only mark jobs as *FIZZLED* when it does not receive this ping from the Rocket for 4 hours. You can test this feature with the following sequence of commands::


    lp_run.py reset <TODAY'S DATE>
    lp_run.py add fw_sleep.yaml
    rlauncher_run.py singleshot
    ---(forcibly close your terminal window)
    ---(wait 4 or more hours!! or temporarily set your System Clock ahead by 5 hours)
    lp_run.py detect_fizzled --fix
    lp_run.py get_fw 1

.. note:: You can shorten the ping times and detection times by editing the settings in the file ``fw_config.py``, but we suggest you leave them alone unless really needed.

Life after *FIZZLED*
====================

Once FireWorks has identified a job as *FIZZLED*, you might wonder what comes next. Currently, your only option is to resubmit your workflow, perhaps with modifications to prevent any problems that might have caused job failure. If you've correctly enabled :doc:`duplicate checking </duplicates_tutorial>`, your new workflow will automatically pick up where you left off, and you won't do any extra calculations. This is the preferred way of dealing with failures. If you haven't enabled duplicate checking, then you'll need to rerun your entire workflow from the beginning, and any steps that came prior to the failure will be repeated unless you omit them from the new workflow.