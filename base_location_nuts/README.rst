NUTS Regions
============

This module allows to import NUTS locations.

Creates two new fields in Partner object:

* Region (res.partner.region): Classification over state, automatically
  calculated when state is selected
* Substate (res.partner.substate): Classification above state, user must select
  one from available for selected state

You need to install another addon (one for each country) in order to use
these NUTS, for example:

* l10n_es_location_nuts :
    * Spanish Provinces (NUTS level 4) as Partner State
    * Spanish Autonomous communities (NUTS level 3) as Partner Substate
    * Spanish Regions (NUTS level 2) as Partner Region
* l10n_de_location_nuts :
    * German states (NUTS level 2) as Partner State
    * German districts (NUTS level 3) as Partner Substate
    * German regions (NUTS level 4) as Partner Region

After installation, you must click at import wizard to populate NUTS items
in Odoo database in:
Sales > Configuration > Address Book > Import NUTS 2013

This wizard will download from Europe RAMON service the metadata to
build NUTS in Odoo. Each localization addon (l10n_es_location_nuts,
l10n_de_location_nuts, ...) will inherit this wizard and
relate each NUTS item with states. So if you install a new localization addon
you must re-build NUTS clicking this wizard again.

Only Administrator can manage NUTS list (it is not neccesary because
it is an European convention) but any registered user can read them,
in order to allow to assign them to partner object.

Credits
=======

Contributors
------------
* Antonio Espinosa <antonioea@antiun.com>
