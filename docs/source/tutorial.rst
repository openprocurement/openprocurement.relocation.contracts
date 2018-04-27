.. _tutorial:

Tutorial
========

When customer needs to change current broker this customer should provide new preferred broker with ``transfer`` key for an object (tender, bid, complaint, etc.). Then new broker should create `Transfer` object and send request with `Transfer` ``id`` and ``transfer`` key (received from customer) in order to change object's owner.

Examples for Contract
---------------------
   
Contract ownership change
~~~~~~~~~~~~~~~~~~~~~~~~~

Let's view transfer example for contract transfer.

Transfer creation 
^^^^^^^^^^^^^^^^^

First of all, you must know ID of the contract that you want to transfer.

Broker that is going to become new contract owner should create a `Transfer`.

.. include:: tutorial/create-contract-transfer.http
   :code:

`Transfer` object contains new access ``token`` and new ``transfer`` token for the object that will be transferred to new broker.

Changing contract's owner
^^^^^^^^^^^^^^^^^^^^^^^^^

In order to change contract's ownership new broker should send POST request to appropriate `/contracts/id/` with `data` section containing ``id`` of `Transfer` and ``transfer`` token received from customer:

.. include:: tutorial/change-contract-ownership.http
   :code:

Updated ``owner`` value indicates that ownership is successfully changed. 

Note that new broker has to provide its customer with new ``transfer`` key (generated in `Transfer` object).

After `Transfer` is applied it stores contract path in ``usedFor`` property.

.. include:: tutorial/get-used-contract-transfer.http
   :code:

Let's try to change the contract using ``token`` received on `Transfer` creation:

.. include:: tutorial/modify-contract.http
   :code:

Contract credentials change
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to get rights for future contract editing, you need to generate Transfer object and then apply this Transfer using the endpoint POST: /contracts/{id}/ownership, where id stands for contract ID.

Create new transfer
^^^^^^^^^^^^^^^^^^^

Let`s generate Transfer.

.. include:: tutorial/create-contract-transfer-credentials.http
   :code:

`Transfer` object contains new ``access.token`` that can be used for further contract modification and new ``transfer`` token.

Changing contract's credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to generate new contract's credentials broker should send POST request to appropriate endpoint /contracts/{id}/ownership with data section containing id of new Transfer generated previously and tender_token.

.. include:: tutorial/change-contract-credentials.http
   :code:

After Transfer is applied it stores contract path in usedFor property and can`t be used for other object.

.. include:: tutorial/get-used-contract-credentials-transfer.http
   :code:

Let's change the contract using ``token`` received on `Transfer` creation:

.. include:: tutorial/modify-contract-credentials.http
   :code:
