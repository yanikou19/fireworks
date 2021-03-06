=================
Dynamic Workflows
=================

Many workflows require some type of dynamicism. For example, a FireWork might need data from a previous FireWork in order to perform its task. The second FireWork won't know what to run until the first one completes. In a more complicated example, we might even want to create new FireWorks automatically depending on the results of the current FireWork.

This tutorial can be completed from the command line, but some knowledge of Python is suggested. In this tutorial, we will run examples on the central server for simplicity. One could just as easily run them on a FireWorker if you've set one up.

A workflow that passes data
===========================
Let's imagine a workflow in which the first step adds the numbers 1 + 1, and the second step adds the number 10 to the result of the first step. The second step doesn't know in advance what the result of the first step will be; the first step must pass its output to the second step after it completes. The final result should be 10 + (1 + 1) = 12. Visually, the workflow looks like:

.. image:: _static/addmod_wf.png
   :width: 200px
   :align: center
   :alt: Add and Modify WF

The text in blue lettering is not known in advance and can only be determined after running the first workflow step. Let's examine how we can set up such a workflow.

1. Move to the ``dynamic_wf`` tutorial directory on your FireServer::

    cd <INSTALL_DIR>/fw_tutorials/dynamic_wf

#. The workflow is encapsulated in the ``addmod_wf.yaml`` file. Look inside this file. Like last time, the ``fws`` section contains a list of FireWork objects:

 * ``fw_id`` -1 looks like it adds the numbers 1 and 1 (defined in the **input_array**) within an ``Add and Modify`` FireTask. This is clearly the first step of our desired workflow. Although we don't yet know what the ``Add and Modify`` FireTask is, we can guess that it at least adds the numbers in the **input_array**.
 * ``fw_id`` -2 only adds the number 10 thus far. It is unclear how this FireWork will obtain the output of the previous FireWork without knowing the details of the ``Add and Modify`` FireTask. We'll explain that in the next step.
 * The second section, labeled ``links``, connects these FireWorks into a workflow in the same manner as the previous example.

#. We pass information by defining a custom FireTask that returns an instruction to modify the workflow. To see how this happens, we need to look inside the definition of our custom ``Add and Modify`` FireTask. Look inside the file ``addmod_task.py``:

 * Most of this FireTask should now be familiar to you; it is very similar to the ``Addition Task`` we investigated when :ref:`customtask-label`.
 * The last line of this file, however, is different. It reads::

        return FWAction('MODIFY', {'sum': m_sum}, {'dict_mods': [{'_push': {'input_array': m_sum}}]})

 * The first argument, *MODIFY*, indicates that we want to modify the inputs of the next FireWork (somehow!)
 * The second argument, *{'sum': m_sum}*, is the data we want to store in our database for future reference. It does not affect this FireWork's operation.
 * The final argument, *{'dict_mods': [{'_push': {'input_array': m_sum}}]}*, is the most complex. This argument describes the modifications to make to the next FireWork using a special language. For now, it's sufficient to know that when using the *MODIFY* command, one must specify a *dict_mods* key that contains a list of *modifications*. In our case, we have just a single modification: *{'_push': {'input_array': m_sum}}*.
 * The instruction *{'_push': {'input_array': m_sum}}* means that the *input_array* key of the next FireWork(s) will have another item *pushed* to the end of it. In our case, we will be pushing the sum of (1 + 1) to the ``input_array`` of the next FireWork.

#. The previous step can be summarized as follows: when our FireTask completes, it will push the sum of its inputs to the inputs of the next FireWork. Let's see how this operates in practice by inserting the workflow in our database::

    lp_run.py reset <TODAY'S DATE>
    lp_run.py add addmod_wf.yaml

#. If we examined our two FireWorks at this stage, nothing would be out of the ordinary. In particular, one of the FireWorks has only a single input, ``10``, and does not yet know what number to add to ``10``. To confirm::

    lp_run.py get_fw 1
    lp_run.py get_fw 2

#. Let's now run the first step of the workflow::

    rlauncher_run.py --silencer singleshot

#. This prints out ``The sum of [1, 1] is: 2`` - no surprise there. But let's look what happens when we look at our FireWorks again::

    lp_run.py get_fw 1
    lp_run.py get_fw 2

#. You should notice that the FireWork that is ``READY`` - the one that only had a single input of ``10`` - now has *two* inputs: ``10`` and ``2``. Our first FireTask has pushed its sum onto the ``input_array`` of the second FireWork!

#. Finally, let's run the second step to ensure we successfully passed information between FireWorks::

    rlauncher_run.py --silencer singleshot

#. This prints out ``The sum of [10, 2] is: 12`` - just as we desired!

You've now successfully completed an example of passing information between workflows! You should now have a rough sense of how one step of a workflow can modify the inputs of future steps. There are many types of workflow modifications that are possible. We will present details in a different document. For now, we will continue by demonstrating another type of dynamic workflow.

A Fibonacci Adder
=================

You may not know in advance how many workflow steps you require to achieve a result. For example, let's generate all the `Fibonacci numbers <http://en.wikipedia.org/wiki/Fibonacci_number>`_ less than 100, but only using a single addition in each FireWork. It's unclear how many additions we'll need, so we can't set up this workflow explicitly.

Instead, we will start with a single FireWork that contains the start of the sequence (0, 1). This FireWork will generate the next Fibonacci number in the sequence by addition, and then *generate its own child FireWork* to carry out the next addition operation. That child will in turn generate its own children. Starting from a single FireWork, we will end up with as many FireWorks as are needed to generate all the Fibonacci numbers less than 100.

A diagram of our the first two steps of operation of our FireWork looks like this:

.. image:: _static/fibnum_wf.png
   :width: 200px
   :align: center
   :alt: Fibonacci Number Workflow

Our single FireWork will contain a custom FireTask that does the following:

* Given two input Fibonacci numbers (e.g., 0 and 1), find the next Fibonacci number (which is equal to their sum, in this case 1).
* If this next Fibonacci number is less than 100 (the **stop_point**):
    * Print it
    * Create its own child FireWork that will sum the new Fibonacci number we just found with the larger of the current inputs. In our example, this would mean to create a new FireWork with inputs 1 and 1.
    * This new FireWork will output the next Fibonacci number (2), and then create its own child FireWork to continue the sequence (not shown)

* When the next Fibonacci number is greater than 100, print a message that we have exceeded our limit and stop the workflow rather than generate more FireWorks.

Let's see how this is achieved:

1. Stay in the ``dynamic_wf`` tutorial directory on your FireServer::

    cd <INSTALL_DIR>/fw_tutorials/dynamic_wf

#. The initial FireWork is in the file ``fw_fibnum.yaml``. Look inside it. However, there is nothing special here. We are just defining the first two numbers, 0 and 1, along with the **stop_point** of 100, and asking to run the ``Fibonacci Adder Task``.

#. The dynamicism is in the ``Fibonacci Adder Task``, which is defined in the file ``fibadd_task.py``. Look inside this file.

 * The most important part of the code are the lines::

        new_fw = FireWork(FibonacciAdderTask(), {'smaller': larger, 'larger': m_sum, 'stop_point': stop_point})
        return FWAction('CREATE', {'next_fibnum': m_sum}, {'create_fw': new_fw})

 * The first line defines a new FireWork that is also a ``Fibonacci Adder Task``. However, the inputs are slightly changed: the **smaller** number of the new FireWork is the larger number of the current FireWork, and the **larger** number of the new FireWork is the sum of the two numbers of the current FireWork (just like in our diagram). The **stop_point** is kept the same.
 * Next, we are returning an instruction to *CREATE* a child FireWork to the workflow.
 * The *{'next_fibnum': m_sum}* portion is just data to store inside the database, it does not affect operation.
 * The *{'create_fw': new_fw}* means that we want to add a single child FireWork, the ``new_fw`` that we just defined in the previous command. The *create_fw* key is a special key that can be defined when returning an *CREATE* instruction. The LaunchPad will interpret this command after the FireWork completes.

#. Now that we see how our FireTask will create a new FireWork dynamically, let's run the example::

    lp_run.py reset <TODAY'S DATE>
    lp_run.py add fw_fibnum.yaml
    lp_run.py get_fw_ids

#. That last command should prove that there is only one FireWork in the database. Let's run it::

    rlauncher_run.py --silencer singleshot

#. You should see the text ``The next Fibonacci number is: 1``. Normally this would be the end of the story - one FireWork, one Rocket. But let's try to again to get all the FireWorks in the database::

    lp_run.py get_fw_ids

#. Now there are *two* FireWorks in the database! The previous FireWork created a new FireWork dynamically. We can now run this new FireWork::

    rlauncher_run.py --silencer singleshot

#. This should print out the next Fibonacci number (2). You can repeat this until our FireTask detects we have gone above our limit of 100::

    $ rlauncher_run.py --silencer singleshot
    The next Fibonacci number is: 3
    $ rlauncher_run.py --silencer singleshot
    The next Fibonacci number is: 5
    $ rlauncher_run.py --silencer singleshot
    The next Fibonacci number is: 8
    $ rlauncher_run.py --silencer singleshot
    The next Fibonacci number is: 13
    $ rlauncher_run.py --silencer singleshot
    The next Fibonacci number is: 21
    $ rlauncher_run.py --silencer singleshot
    The next Fibonacci number is: 34
    $ rlauncher_run.py --silencer singleshot
    The next Fibonacci number is: 55
    $ rlauncher_run.py --silencer singleshot
    The next Fibonacci number is: 89
    $ rlauncher_run.py --silencer singleshot
    We have now exceeded our limit; (the next Fibonacci number would have been: 144)

#. If we try to run another Rocket, we would get an error that no FireWorks are left in the database (you can try it if you want). We'll instead look at all the different FireWorks created dynamically by our program::

    lp_run.py get_fw_ids

There are 11 FireWorks in all, and 10 of them were created by other FireWorks rather than a human!

A Fibonacci Adder: The Quick Way
================================

Let's see how quickly we can add and run our entire workflow consisting of 11 steps::

    lp_run.py add fw_fibnum.yaml
    rlauncher_run.py --silencer rapidfire

That was quick!

.. note:: The rapidfire option creates a new directory for each launch. At the end of the last script you will have many directories starting with ``launcher_``. You might want to clean these up after running (or store them for future provenance!)

The end is just the beginning
=============================

You've made it to the end of the core tutorial! By now you should have a good feeling for the basic operation of FireWorks and the types of automation it allows. However, it is certainly not the end of the story. Job priorities, duplicate job detection, and running through queues are just some of the features we haven't discussed in the core tutorial.

If you are already itching to learn more about additional topics, please follow the additional tutorials on our main page. Otherwise, have fun playing with FireWorks! As always, let us know what you think.