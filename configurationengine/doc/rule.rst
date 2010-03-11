Rule
====

	A Configuration can contain rule's, which can be aplied to the :class:`~cone.public.api.Configuration` 
	:class:`~cone.public.api.Feature`'s. In ConE a single rule will create an instance of :class:`~cone.public.plugin.Relation`. 
	
	The textual format of a rules is always of form:
	::
	
	  <left side> relation_name <right side>.

The rule dialect
----------------
	
	The features are accessed in the left and right side of the rule with the default :class:`~cone.public.api.View` of the :class:`~cone.public.api.Configuration`. 
	Basically ConE will get the default_view and use the :class:`~cone.public.api.ObjectContainer` member access to retrieve the feature.
	There are few special characters that are converted to function calls in the rule transformation.
	
	* ``*`` => refers to all immediate childer of this node, which is transformed to method call :meth:`cone.public.api.ObjectContainer.__objects__`
	* ``**`` => refers to all childer of this node, which is transformed to method call :meth:`cone.public.api.ObjectContainer.__traverse__`
	
	Both sides of the rule are something that the :class:`~cone.public.plugin.Relation` will somehow evaluate. How the left 
	side and right side are evaluated, is basically specific to the implementation of the :meth:`~cone.public.plugin.Relation.execute` 
	method of the :class:`~cone.public.plugin.Relation`. However certain basic evaluation rules apply to all :class:`~cone.public.plugin.Relation` objects.
	
	When a feature is referred, ConE will try to return the value of the feature. 
	Then the Relation tries to evaluate if the given feature is bound and evaluates as True.
	
	So for example referring to a feature.
	
	``group.fea1`` is the same as writing ``group.fea1==True`` for a boolean feature.
	``group.intfea1`` is the same as writing ``group.fea1!=0`` for a integer feature.
	
	If a feature is unbound, trying to access its value will raise UnboundError. 

Boolean logic in rules
----------------------
	
		Both left and right side of the rule can contain normal boolean algebra that is utilized in the evaluation. This uses 
		default python syntax for boolean logic, with keywords *and*, *or*, *not*.

Example of boolean logic
^^^^^^^^^^^^^^^^^^^^^^^^  
::
	a.b and c.d=10 depends (not a.b.x=10 or a.b.x=0)




Rules with different multiplicity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	The above mechanism enables that the rules can define relations with different multiplicity. 
	
	* one-to-one
	
		* e.g. A depends B
	
	* one-to-many
	
		* e.g. A depends B.*, which is basically the same as wrinting A depends (B.child1 and B.child2 and ..)
		* e.g. A depends B and C
	
	* many-to-one
	
		* e.g. A.* depends B
	
	* many-to-many
	
		* e.g. A.* depends B.*

Examples
--------
	
	* A.B.C requires A.B.D
	* fea.group.* requires fea.group
	* wlan.setting maps voip.setting=10
