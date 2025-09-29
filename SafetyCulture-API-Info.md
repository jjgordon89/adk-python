Introduction
Getting started with SafetyCulture's API

This portal provides resources to learn and get started with the SafetyCulture (formerly iAuditor) API.

Access to the API requires a Premium or Enterprise Plan. You can sign up and upgrade to trial our Premium Plan for 30 days, or contact us to find out more about our Enterprise Plan.

Generate an authorization token (API token)
The API requires an authorization token (API token) for each request. A token can be generated from your SafetyCulture account.

🚧
Please note that API tokens expire after 30 days of inactivity, at which point you would need to generate a new token to use. If a token is used to make API requests within that period, then it would not expire unless it's made invalid from new tokens.

Once you've obtained a token, it needs to be passed in the Authorization header on requests to the API. For example, Authorization: Bearer b7f8f791...f26e554d.

The SafetyCulture API uses OAuth 2.0 as the means of authorization for individual requests. The initial authorization uses the Resource Owner Password Credentials Grant method and currently doesn't support any other flows.

The token used by the API is a Bearer token. It should be considered as a "personal access token" that you control yourself, for your own SafetyCulture account. A pre-registered client ID and secret are not required to create an authorization token.

Authorize a request
Shell

curl "https://api.safetyculture.io/audits/search?field=audit_id" \
  -H "Authorization: Bearer {api_token}"
You can make requests to the API by passing the authorization token in the Authorization HTTP header, following the format Authorization: Bearer b7f8f791...f26e554d. This header needs to be passed on every request.

If a request doesn't have the Authorization header, the API would return a 401 HTTP error code to indicate an unauthorized request.

Sample requests in this guide present the Authorization header with Bearer {api_token}. If you're using sample requests to try the API, remember to replace {your access token} with your access token.

Search for inspections
Shell

curl "https://api.safetyculture.io/audits/search?field=audit_id&field=modified_at" \
  -H "Authorization: Bearer {api_token}"
JSON

{
  "count": 2,
  "total": 2,
  "audits": [
    {
      "audit_id": "audit_01ca38a821504cda885736cccbb9ba40",
      "modified_at": "2015-03-17T03:16:31.072Z"
    },
    {
      "audit_id": "audit_853C17E6040B43DA1DFDDD8E6A4D6D3A",
      "modified_at": "2015-03-24T06:31:47.203Z"
    }
  ]
}
To search for inspections using the API, make a GET request to the https://api.safetyculture.io/audits/search endpoint. By default, the response lists inspections in ascending order, from the oldest to the most recently modified, limited to the first 1,000 inspections.

You can pass the fields you want to see in the response, as well as the parameters to apply and narrow the search. See the Search modified inspections section for more information on search parameters.

📘
You must pass at least the audit_id field to a search inspections request, otherwise the API would return a 400 HTTP error code to indicate a bad request.

Search inspections within a given period

Shell

curl "https://api.safetyculture.io/audits/search?field=audit_id&field=modified_at&modified_after=2015-01-01T00:00:00.000Z&modified_before=2015-04-01T00:00:00.000Z" \
  -H "Authorization: Bearer {api_token}"
Search inspections conducted from a specific template

Shell

curl "https://api.safetyculture.io/audits/search?field=audit_id&template=template_37afc5890aa94e778bbcde4fc4cbe480" \
  -H "Authorization: Bearer {api_token}"
📘
All date/time values in requests and responses are in Coordinated Universal Time (UTC), following the ISO 8601 date and time format.

Retrieve an inspection
Shell

curl "https://api.safetyculture.io/audits/audit_01ca38a821504cda885736cccbb9ba40" \
  -H "Authorization: Bearer {api_token}"
JSON

{
  "template_id": "template_BB29F82814B64F559A33BF7CAA519787",
  "audit_id": "audit_01ca38a821504cda885736cccbb9ba40",
  "created_at": "2015-05-01T01:13:20.584Z",
  "modified_at": "2015-06-30T05:03:40.754Z",
  "audit_data": {...}
}
Once you have the list of inspections, you can retrieve each inspection individually using the
https://api.safetyculture.io/audits/<audit_id> endpoint. You can find an inspection's audit_id either from a previous search or via the web app.

Each successful request's JSON response for this endpoint is a complete representation of the inspection data, including the template that was used. See the inspection format section for more information.

Sample response: Any media attachments are also included

JSON

    {
      "media": [
        {
          "date_created": "2015-06-24T22:59:59.000Z",
          "file_ext": "jpg",
          "label": "no label",
          "media_id": "9E3BD015-6275-4668-BAF1-296B2F38444C",
          "href": "https://api.safetyculture.io/audits/audit_01ca38a821504cda885736cccbb9ba40/media/9E3BD015-6275-4668-BAF1-296B2F38444C"
        }
      ]
    }
As you can see in the media attachments sample response, the media references can be used if you want to retrieve the media using the API.

Retrieve a media item from an inspection
Shell

curl "https://api.safetyculture.io/audits/audit_01ca38a821504cda885736cccbb9ba40/media/9E3BD015-6275-4668-BAF1-296B2F38444C" \
  -o 9E3BD015-6275-4668-BAF1-296B2F38444C.jpg \
  -H "Authorization: Bearer {api_token}"
📘
For this endpoint, the request returns the actual media file with the relevant Content-Type header instead of JSON.

Once you've retrieved an inspection, you may also want to retrieve any media item attached in the inspection, such as photos, annotations, and PDFs. You can retrieve a media item by passing the inspection's audit_id and the media item's media_id.

Each request downloads the media item directly, so make sure to save the output with an appropriate name and the correct file extension. You can use the values from the media item in the inspection JSON to construct the filename, such as <media_id>.<file_ext>.

Repeat this request for as many inspection media items as you require.

Next steps
By now, you should have a basic understanding of the inspection retrieval methods using the SafetyCulture API. You can continue to learn about all the available requests and parameters or take a look at some API use cases that you might like to try yourself.

Authentication
Connecting securely to SafetyCulture's API

The API requires an authorization token for each request. A token can be generated from your SafetyCulture account.

🚧
Please note that API tokens expire after 30 days of inactivity, at which point you would need to generate a new token to use. If a token is used to make API requests within that period, then it would not expire unless it's made invalid from new tokens.

Once you've obtained a token, it needs to be passed in the Authorization header on requests to the API. For example, Authorization: Bearer b7f8f791...f26e554d.

The SafetyCulture API uses OAuth 2.0 as the means of authorization for individual requests. The initial authorization uses the Resource Owner Password Credentials Grant method and currently doesn't support any other flows.

The token used by the API is a Bearer token. It should be considered as a "personal access token" that you control yourself, for your own SafetyCulture account. A pre-registered client ID and secret are not required to create an authorization token.

Get modified inspections
Retrieve updates about your SafetyCulture data

Once you have extracted all of the historical data, the next obvious step is to retrieve the modified inspections so that you can continue populating your own systems with new inspection data. This function is also useful for producing regular updates from your inspection data, such as a live dashboard.

We recommend that you use webhooks and subscribe to specific events. Alternatively, you can use polling against the following endpoint:

Shell

curl "https://api.safetyculture.io/audits/search?field=audit_id&field=modified_at&modified_after=2015-03-24T06:31:47.203Z" \
  -H "Authorization: Bearer {api_token}"
To do this, you will search for inspections that are either after the last inspection that you have, or the last time you attempted to retrieve new inspections, using the modified_after parameter.

JSON

{
  "count": 1,
  "total": 1,
  "audits": [
    {
      "audit_id": "audit_853C17E6040B43DA1DFDDD8E6A4D6D3A",
      "modified_at": "2015-03-24T06:31:47.203Z"
    }
  ]
}
This will retrieve only the inspections modified since you last retrieved data, and often may contain no inspections at all depending on the frequency of updates and the frequency data is retrieved. With this information, you may then follow the steps from the previous use case to retrieve the inspection content and media.

Note that the inspections retrieved in this request may return identifiers that you have previously retrieved if the inspection it points to has been modified. You should ensure that this overwrites any inspection data that exists in your own system rather than duplicating them.

Start and pre-fill inspections
Automatically start inspections with pre-filled answered questions

Being able to start and share inspections automatically makes it easier for developers to build custom solutions that:

schedule inspections to be created at particular times,
pre-fill inspection information from external data sources or from previously completed inspections,
trigger custom actions like reminders or other notifications from third-party providers to be executed before and/or after inspections get created
and more.

With automation services (like Zapier, IFTTT, MS Flow etc.) work flows similar to the above can be achieved without any development effort.

One common use case example is where a supervisor wants an inspection to start automatically and be assigned to a team member to conduct at a particular time or on a recurring schedule. To save time, reduce human error and increase consistency, any responses that are known at the time the inspection is started should be automatically pre-filled. Such responses could include an equipment serial number, the full name of the person intended to complete the inspection, the inspection site or anything else relevant to the task at hand.

The API can be used to achieve such a scenario in 3 steps:

Start an inspection to create an inspection against a specified template
List group or organization users (or List groups) to discover the IDs of the users (or groups) to share the inspection with in order to conduct it
Share an inspection with the IDs from the previous step
If the user/group IDs to share the inspection with are already known, the second step is not needed and the process can be simplified to two steps:

Start an inspection to create an inspection against a specified template
Share an inspection with the users or groups you want to conduct it.
Depending on the access you assign at the time of sharing, you may restrict some users' access to view only, edit to allow users to conduct the inspection, or delete to also permit users to delete the shared inspection. The person conducting the inspection doesn't need access to the template which also avoids the possibility of inspections getting started (e.g. using the SafetyCulture mobile app) outside the control of the supervisor.

In our example use case above, the supervisor creating the inspection will always be the owner of the created inspection but may not always be the author as well. The author of the created inspection is the last user who made any change to the inspection.

Any "auto-sharing" properties configured in the template that was used to start the inspection are inherited at inspection creation time so the inspection is automatically shared with the users and groups configured within the template. For instance, in our use case above, the supervisor creating the inspection may have configured the template so that inspections created from it are automatically shared with the management group.

Now that an inspection can be started and shared automatically, the supervisor may decide they want an inspection to start at pre-configured regular (or irregular) times e.g. a weekly inspection from the "Weekly Checklist" template every Monday at 11am etc. This can be achieved very easily by setting up a scheduled job (using any third party scheduler software like cron, Windows Scheduled Tasks, Zapier etc.) that triggers calls to the Start an inspection and Share an inspection API endpoints as shown above.

Especially in the case of repeatedly conducted inspections, it can be a tedious task to copy information from other systems or from previous inspection responses to pre-fill certain items of the newly created inspection. Pre-filling such information using the API makes this problem go away for many types of inspection responses. In our example use case above, the supervisor could maintain a database of equipment that needs to be inspected when a work order is generated by a field worker against a particular part or equipment. An inspection gets automatically created as a result and shared with the user to conduct the inspection. The inspection title, equipment location, serial number and description of the work order are pre-filled into the inspection so the inspector does not have to find and fill in that information manually, thus saving time and avoiding typing and consistency mistakes.

Step by step implementation
Let's assume the supervisor of our use case above want to schedule an inspection for equipment with serial number "SC-8799229947729942245".

The supervisor's SafetyCulture account is used to obtain an API access token used to perform all API interaction below.

A particular template is to be used for inspecting that sort of equipment, so the supervisor uses the Search modified templates API call to find the ID of the template to use.

Searching for the template ID to use

Shell

curl "https://api.safetyculture.io/templates/search?field=template_id&field=name" \
  -H "Authorization: Bearer {api_token}"
The above command returns the template ID corresponding to the template name for each template on the supervisor's account

JSON

{
  "count": 1,
  "total": 1,
  "templates": [
    {
      "template_id": "template_BB29F82814B64F559A33BF7CAA519787",
      "name": "Equipment Inspection Template"
    }
  ]
}
With the template ID and Start an inspection API capability, the supervisor requests from the API to start an inspection and pre-fill the inspection title response with

the equipment serial number
the name of the person to conduct the inspection (note: not shared with them yet, will do in the next step)
Create a new inspection from template_BB29F82814B64F559A33BF7CAA519787 with pre-filled information

Shell

curl -X POST "https://api.safetyculture.io/audits" \
-d '{
       "template_id": "template_BB29F82814B64F559A33BF7CAA519787",
       "header_items": [
         {
           "item_id": "f3245d40-ea77-11e1-aff1-0800200c9a66",
           "label": "Inspection Title",
           "type": "textsingle",
           "responses": {
             "text": "Equipment Inspection S/N SC-8799229947729942245"
           }
         },
         {
           "item_id": "f3245d43-ea77-11e1-aff1-0800200c9a66",
           "label": "Conducted By",
           "type": "textsingle",
           "responses": {
             "text": "John Citizen"
           }
         }
       ]
     }' \
-H "Content-Type: application/json" \
-H "Authorization: Bearer {api_token}"
The above command returns the JSON content of the created inspection (some fields omitted for brevity)

JSON

{
  "template_id": "template_BB29F82814B64F559A33BF7CAA519787",
  "audit_id": "audit_01ca38a821504cda885736cccbb9ba40",
  "created_at": "2017-01-25T01:13:20.584Z",
  "modified_at": "2017-01-25T01:13:20.584Z",
  "audit_data": {...},
  "template_data": {...},
  "header_items": [...],
  "items": [...]
}
The supervisor records the audit_id from the API response to use in a later step.

The owner and author of the created inspection are both the supervisor at this stage. The new inspection is immediately accessible (e.g. in SafetyCulture or via Search modified inspections) to any users configured to have access to it via the template's "auto-sharing" properties, if any were set.

Now the supervisor wants to "assign" the inspection to team member named John Citizen with email address "john.citizen@safetyculture.io" who do not have access to "Equipment Inspection Template" at all. To share the inspection with John Citizen the supervisor looks up their user ID using the List group or organization users API capability.

Lookup the user ID of the person to conduct the inspection

Shell

curl -X POST "https://api.safetyculture.io/users/search" \
-d "{"email": ["john.citizen@safetyculture.io"]}}" \
-H "Authorization: Bearer {api_token}"
The above command returns the user ID of John Citizen:

JSON

{
  "users": [
    {
      "id": "user_c4e2421223b5497186bb8ea4e4159fcc",
      "email": "john.citizen@safetyculture.io",
      "firstname": "John",
      "lastname": "Citizen"
    }
  ]
}
With the audit_id and user_id from the previous steps the supervisor can now share the newly created inspection with John Citizen using the Share an inspection API capability. Sharing with edit access allows John Citizen to complete the inspection but not delete it for increased security.

Share the created inspection with John Citizen (user_c4e2421223b5497186bb8ea4e4159fcc) with edit access level.

Shell

curl -X POST "https://api.safetyculture.io/audits/audit_01ca38a821504cda885736cccbb9ba40/share" \
-d '{"shares": [{"id":"user_c4e2421223b5497186bb8ea4e4159fcc", "permission":"edit"}]}' \
-H "Content-Type: application/json" \
-H "Authorization: Bearer {api_token}"
John Citizen can now see and conduct the inspection using SafetyCulture which makes him the author of the inspection. The supervisor remains the owner and maintains access to the inspection at all times.

Update inspection responses based on selected responses
Automatically modify inspection responses based on specific responses within the inspection.

This guide explains how to automatically update inspection responses based on specific responses selected during the inspection. For example, you would like to update the Site name and Site manager fields based on the user's answer in the site response type. This approach is helpful for auto-filling data from external systems like location or client details to reduce manual entry and create custom calculations based on inspection data.

🚧
Changes made via the API will not be visible in an open inspection until the user exits and reopens it.

You can update inspection responses automatically in three steps:

Register a webhook and receive inspection events.
Fetch the information to update in the inspection
Update the inspection responses.
Register a webhook and receive inspection events
SafetyCulture offers various webhooks to notify you of platform events. For this scenario, use the TRIGGER_EVENT_INSPECTION_ITEM_UPDATED event, which tracks when an inspection item is updated. Once it is updated, your server receives a POST request with the relevant event data.

Shell

curl --request POST \
     --url https://api.safetyculture.io/webhooks/v1/webhooks \
     --header 'accept: application/json' \
     --header 'authorization: Bearer {api_token}' \
     --header 'content-type: application/json' \
     --data '
{
  "trigger_events": [
    "TRIGGER_EVENT_INSPECTION_ITEM_UPDATED"
  ],
  "url": "https://example.com"
}
'
Upon any inspection completion, your server will receive an HTTP POST request with a payload similar to the following:

JSON

{
  "webhook_id": "d1ddb5d8-8ee0-41c7-bda5-cfab6740d465",
  "version": "3.0.0",
  "event": {
    "date_triggered": "2024-05-22T04:11:15Z",
    "event_types": [
      "TRIGGER_EVENT_INSPECTION",
      "TRIGGER_EVENT_INSPECTION_ITEM_UPDATED",
      "TRIGGER_EVENT_INSPECTION_ITEM_SITE"
    ],
    "triggered_by": {
      "user": "user_f2dad30f787b4b5da890655ab8ac8ddf",
      "organization": "1deba7cb-6354-4377-9c35-7ccb56180d4e"
    }
  },
  "resource": {
    "id": "audit_b432cc30787c4606a08645552a24193a",
    "type": "INSPECTION"
  },
  "data": {
    "inspection_site_set": {
      "site": {
        "folder_id": "c1293ede-04ca-4be5-bd90-bc6ea01360b6"
      }
    },
    "details": {
      "inspection_id": "audit_b432cc30787c4606a08645552a24193a",
      "template_id": "template_eebb5009bdd247f783c9db74ce578a92",
      "org_id": "1deba7cb-6354-4377-9c35-7ccb56180d4e",
      "modify_time": "2024-05-22T04:11:15.618Z",
      "canonical_start_time": "2024-05-22T04:11:08.838Z",
      "score": {}
    }
  }
}
📘
The payload will vary depending on the type of question answered. In this example, the payload is associated with setting a site question.

Fetch the information to update in the inspection
Use the selected site ID from the event payload to retrieve the information you want to update in the inspection. This step varies based on your data source.

Update the inspection responses
To identify the item_id to update, you can use the Get an inspection API with an example inspection ID. This will return the item_id and label in a given inspection.

Shell

curl --request PUT \
     --url https://api.safetyculture.io/audits/{inspection_id} \
     --header 'accept: application/json' \
     --header 'authorization: Bearer {api_token}' \
          --data '
{
  "items": [
    {
      "type": "text",
      "responses": {
        "text": "Sydney - Site XYZ"
      },
      "item_id": "d0e3e7aa-03ed-43ea-867e-b61ece76f099"
    },
    {
      "type": "text",
      "responses": {
        "text": "Joe Bloggs"
      },
      "item_id": "d5cc82a1-c1cb-4543-9bab-4422f53f88ee"
    }
  ]
}
'
See Update an inspection for more details on updating an inspection.

A complete example of this might look like this:

JavaScript

// https://developer.safetyculture.com/reference/authentication
const ACCESS_TOKEN = 'my-access-token';

// Templates we want to run this integration against
const TEMPLATE_IDS = [
  'template_eebb5009bdd247f783c9db74ce578a92',
  'template_xyx123'
]

// The item ID for "Site Name"
const ITEM_ID_SITE_NAME = 'd0e3e7aa-03ed-43ea-867e-b61ece76f099';
// The item ID for "Site Manager"
const ITEM_ID_SITE_MANAGER = 'd5cc82a1-c1cb-4543-9bab-4422f53f88ee';

// The payload received from https://developer.safetyculture.com/reference/webhooks
async function receiveSafetyCultureWebhook(payload) {
  // Only listen to events where a site has been updated.
  if (!payload.data.inspection_site_set) {
    return;
  }

  // Only listen to events for a specific templates in SafetyCulture.
  if (TEMPLATE_IDS.includes(payload.details.template_id)) {
    return;
  }
  
  const inspection_id = payload.details.inspection_id;
  const site_id = payload.data.inspection_site_set.site.folder_id;

  // retrieve the site details from our internal system.
  // This should be replaced with the system containing that information.
  const siteDetails = await myApi.getSiteDetails(site_id);
  
  // Retrieve the current owner of the inspection.
  const response = await fetch(`https://api.safetyculture.io/audits/${inspection_id}`, {
    method: 'GET',
    headers: {
      accept: 'application/json',
      authorization: `Bearer ${ACCESS_TOKEN}`
    }
  });
  const inspection = await response.json();
  const owner_id = inspection.audit_details.authorship.owner_id;

  // Reassign the ownership.
  await fetch(`https://api.safetyculture.io/audits/${inspection_id}`,  {
    method: 'PUT',
    headers: {
      accept: 'application/json',
      'content-type': 'application/json',
      authorization: `Bearer ${ACCESS_TOKEN}`
    },
    body: JSON.stringify({
      items: [
        {
          type: 'text',
          responses: {text: siteDetails.name},
          item_id: ITEM_ID_SITE_NAME
        },
        {
          type: 'text',
          responses: {text: siteDetails.manager},
          item_id: ITEM_ID_SITE_MANAGER
        }
      ]
    })
  });
}


List groups
get
https://api.safetyculture.io/groups
Retrieves a list of all groups in an organization.

Provides a complete list of all groups within your organization, which is useful for managing organizational structures, roles, and permissions.

Requirements
"Platform management: Groups" permission
Responses

Assets
The SafetyCulture API gives you the ability to list, add, update, and delete assets.

Asset format
This section describes the complete format of an asset.

Asset top level
Describes the top level details of an asset.

JSON

{
  "id":  "0c2100df-3206-4d41-bc08-2c960233114e",
  "code":  "0000443d-a0b0-4135-a9d5-88ff8baf371a",
  "type":  {
    "name":  "Car",
    "type_id":  "f0186762-7675-4628-8071-fd60d6d00613"
  },
  "fields":  [
    {
      "name":  "Brand",
      "string_value":  "Toyota",
      "field_id":  "ef1223ac-dfb5-11ec-9d64-0242ac120001"
    },
  ],
  "created_at":  "2022-04-04T07:12:40.736163Z",
  "modified_at":  "2022-07-26T09:12:23.655252Z",
  "site":  {
    "id":  "cb4c0d0a-49b4-4a58-8b4d-3b28f2dc2fa5",
    "name":  "Sydney HQ"
  },
  "profile_image":  {
    "id":  "026c6df5-c018-413e-aceb-5d4b9a2e842b",
    "token":  "1a38755ad36c62439cba05eb01afd74ac12b2b8df1fcf5f19c29768792c931c4",
    "filename":  "asset.jpeg",
    "media_type":  "MEDIA_TYPE_IMAGE"
  },
  "state":  "ASSET_STATE_ACTIVE"
}

Key	Type	Description
id	string (UUID)	The unique identifier of an asset. This ID is system-generated.
code	string	The user-defined unique identifier of an asset. This ID is user-generated.
type	object	The asset type of an asset.
fields	array	The associated fields of an asset contained in an array as objects. Each asset's fields are based on its asset type.
site	object	The assigned site of an asset contained in an array. If an asset is not assigned to a site, the API will return nil.
state	string	The indicator for whether an asset is active or archived. Refer to asset state for potential values.
created_at	String (ISO8601)	The date created timestamp of an asset.
modified_at	String (ISO8601)	The date last modified timetstamp of an asset.
profile_image	object	The profile picture of an asset contained in an array. If an asset doesn't have a profile picture, the API will return nil.
media	array	The attached media files of an asset contained in an array as objects.
Asset type
Describes the values of an asset type.

JSON

{
  "id": "ff1223ac-dfb5-11ec-9d64-0242ac120001",
  "name": "Air compressor"
}
Key	Type	Description
type_id	string(UUID)	The unique identifier of an asset type. This ID is system-generated.
name	string	The name of an asset type.
Asset field
Describes the values of an asset field.

Key	Type	Description
field_id	string(UUID)	The unique identifier of an asset field. This ID is system-generated.
name	string	The name of an asset field.
string_value	string	The string value of an asset field. This attribute is only used for asset fields using the FIELD_VALUE_TYPE_STRING type.
money_value	s12.common.Money	The money value of an asset field. This attribute is only used for asset fields using the FIELD_VALUE_TYPE_MONEY type.
timestamp_value	Timestamp	The timestamp value of an asset field. This attribute is only used for asset fields using the FIELD_VALUE_TYPE_TIMESTAMP type.
Asset site
Describes the values of a site that's assigned to an asset.

Key	Type	Description
id	string(UUID)	The unique identifier of a site. This ID is system-generated.
name	string	The name of a site.
Asset state
Describes the state of an asset. Either active or archived.

Name	Description
ASSET_STATE_ACTIVE	Indicates that an asset is active.
ASSET_STATE_ARCHIVED	Indicates that an asset is archived.
Asset field types
Describes each type of asset field.

Name	Description
FIELD_VALUE_TYPE_STRING	This type accepts plain text values.
FIELD_VALUE_TYPE_MONEY	This type accepts numerical values with currency codes. For example, "99.99" numerical value with "AUD" as the currency code.
FIELD_VALUE_TYPE_TIMESTAMP	This type accepts timestamp values in the ISO8601 format.
Asset type fields
Describes the association between an asset type and an asset field.

Key	Type	Description
field_id	string(UUID)	The unique identifier of an asset field. This ID is system-generated.
name	string	The name of an asset field.
visible	boolean	The indicator for whether an asset field is visible for an asset type. A true value indicates that an asset field is associated with the retrieved asset type. A false value indicates otherwise.

Inspections
This API provides a number of interfaces to interact with your inspection data.

It is recommended you have the View all data permission if you want a read-only view of your data, or the Manage all data permission if you want to update data. Without these permissions you may not have access to all of the data that belongs to your organization.

Learn more about permissions in SafetyCulture.

Inspection format (legacy)
Top level
JSON

{
  "audit_id": "audit_50ba581235704a368d025056a583aa8b",
  "template_id": "template_4183bcc822f146d3be542118d3f15971",
  "archived": false,

  "created_at": "2015-06-04T02:34:25.000Z",
  "modified_at": "2015-06-04T02:39:21.000Z",

  "audit_data": {},
  "template_data": {},

  "header_items": [{}],
  "items": [{}]
}
Key	Type	Description
audit_id	String	The inspection's ID
template_id	String	ID of the parent template
archived	Boolean	Is the inspection archived or not
created_at	String	ISO date and time when the inspection was first synced to the cloud or created on SafetyCulture
modified_at	String	ISO date and time when the inspection was last synced to the cloud or modified on SafetyCulture
audit_data	Object	General information about the inspection (dates, author, scores, GPS location, etc.)
template_data	Object	Some information on the template (predefined response sets, author, images, etc.)
header_items	Array	Inspection header items (first page, optional)
items	Array	Items in all sections after the header (basically the answers to the questions and other line items)
Inspection data
.audit_data

Inspection data root
JSON

{
  "name": "title",
  "score": 10,
  "total_score": 21,
  "score_percentage": 25,
  "date_completed": "2015-06-04T02:38:02.000Z",
  "date_modified": "2015-06-04T02:38:11.000Z",
  "duration": 224,
  "authorship": {},
  "date_started": "2015-06-04T02:34:25.000Z",
  "location": {},
  "site": {}
}
Key	Type	Description
name	String	Name of the inspection
score	Double	Score of the inspection
total_score	Double	The maximum possible score
score_percentage	Double	A value 0 to 100 calculated as score/total_score
duration	Double	Time taken to complete the inspection (on a device or on SafetyCulture) in seconds
date_started	String	A time and date when the inspection was started (on a device or on SafetyCulture)
date_modified	String	A time and date when the inspection was last modified (on a device or on SafetyCulture)
date_completed	String	A time and date when the inspection was completed (on a device or on SafetyCulture)
authorship	Object	Information on the authorship of the inspection
location	Object	The device (GPS) location of where the inspection was started and completed (if GPS was enabled on the device)
site	Object	The site that was selected for the inspection by the user (if one was selected)
GPS location
.audit_data.location

JSON

{
  "location": {
    "started": {
      "accuracy": 21,
      "geometry": {
        "type": "Point",
        "coordinates": [151.2103808, -33.8846905]
      }
    },
    "completed": {
      "accuracy": 21.189,
      "geometry": {
        "type": "Point",
        "coordinates": [151.2103808, -33.8846905]
      }
    }
  }
}
Authorship
.audit_data.authorship

JSON

{
  "authorship": {
    "owner": "Edward Stark",
    "owner_id": "user_82465b736bb94071a9a47998cf5d7777",
    "device_id": "81A34706-7417-4D6F-8C61-50AC2C814755",
    "author": "Jon Snow",
    "author_id": "user_82465b736bb94071a9a47998cf5d7777"
  }
}
Key	Type	Description
author	String	The person who last made changes to the inspection. Initially it's the same as the owner.
author_id	String	The ID of the inspection author.
owner	String	The person who created the inspection is the original owner of the inspection. The owner can transfer ownership to any other person in the organization via the web app.
owner_id	String	The ID of the inspection owner.
device_id	String	The ID of the device which was used to create the inspection. Generated when the app is installed
Site
.audit_data.site contains information about the site that was selected when starting or editing an inspection. Sites belong to an area, which in turn belongs to a region.

JSON

{
  "site": {
    "name": "Sydney",
    "area": {
      "name": "NSW"
    },
    "region": {
      "name": "AU"
    }
  }
}
Key	Type	Description
name	String	Name of the site.
area	Object	The area that the site belongs to, which in turn belongs to the region.
region	Object	The region that the site and area belong to.
.audit_data.site.area

Key	Type	Description
name	String	Name of the area.
.audit_data.site.region

Key	Type	Description
name	String	Name of the region.
Template data
.template_data

Template data root
JSON

{
  "metadata": {},
  "authorship": {},
  "response_sets": {}
}
Key	Type	Description
metadata	Object	Some metadata about the template (name, description, image, etc.)
response_sets	Object	The question responses attached to the template. (Yes/No/NA, Safe/At Risk/NA, etc.)
authorship	Object	Information on the authorship of the template. Same as inspection authorship.
Template metadata
.template_data.metadata

JSON

{
  "name": "name",
  "description": "description",
  "image": "52ED0287-93F1-4F53-B2C2-29EA3A2423E7"
}
Key	Type	Description
name	String	The template name
description	String	The template description
image	Object	The logo (media) of the template used to create this inspection
Response sets
.template_data.response_sets - The keys used in the object are the IDs of the stored responses. The values of the object are the sets themselves.

JSON

{
  "8a0161b0-a97d-11e4-800b-8f525e51b36e": { "id": "8a0161b0-a97d-11e4-800b-8f525e51b36e", "responses": [] },
  "ec410dd0-a97d-11e4-800b-8f525e51b36e": { "id": "ec410dd0-a97d-11e4-800b-8f525e51b36e", "responses": [] }
}
Response set
.template_data.response_sets.*

JSON

{
  "id": "8a0161b0-a97d-11e4-800b-8f525e51b36e",
  "responses": [{}]
}
Key	Type	Description
id	Object	ID of the response set
responses	Array	Array of response set items
####### Response sets response

.template_data.response_sets.*.responses most of the fields can be absent.

JSON

{
  "id": "22a409a8-c02a-44d5-8b61-e66b6996927e",
  "colour": "5,255,84",
  "enable_score": true,
  "label": "At risk",
  "score": 1,
  "short_label": "R",
  "type": "list"
}
Key	Type	Description
id	String	ID of the response
colour	String	RGB colour of the response button when selected. I.e. "0,0,0" is black, "255,255,255" is white.
enable_score	Boolean	If Score checkbox is checked. Can be attached to any response type
label	String	Label of the response (e.g. 'Yes')
score	Number	Score of the response
short_label	String	Short label of the response (e.g. 'Y')
type	String	The response type. Can only be "question" (single selection) or "list" (multi choice)
Inspection header items
.header_items

Same structure as Inspection Items. See below.

Inspection items
.items are the responses or selections made by the person conducting the inspection.

Item root
JSON

{
  "label": "Inspection",
  "item_id": "379d3910-d2e2-11e4-9038-695120da729f",
  "action_item_profile_id": [],
  "type": "checkbox",
  "parent_id": "a78337ce-2cf2-419b-85b5-c81cd2d68090",
  "options": {},
  "responses": {},
  "media": {},
  "children": ["C5404AC4-2844-4D5A-A02C-9921B9B384C6"],
  "scoring": {}
}
Key	Type	Description
item_id	String	The UUID of the item
parent_id	String	Parent item ID. Can be null
label	String	The text label of the item
type	String	One the the following: information, smartfield, checkbox, media, textsingle, element, primeelement, dynamicfield, category, section, text, signature, switch, slider, drawing, address, list, question, datetime, weather, scanner
options	Object	A set of different options available to that type. Like: min/max values, condition, signature, media, various flags, etc.
responses	Object	Represents user selections. Like value, or list item, or photo, location, date-time, etc.
media	Array	Information about one or more image or photo files
children	Array	The list of child item IDs
scoring	Object	An object containing all the related scores of this item
Deprecated properties that may appear in older inspections but are no longer used

action_item_profile_id | Array | The IDs of any follow up tasks added to this item

Item options
.items[].options most of the fields are absent usually.

JSON

{
  "condition": "3d346f01-e501-11e1-aff1-0800200c9a66",
  "drawing_base_image": {},
  "element": "Truck 1",
  "enable_date": true,
  "enable_signature_timestamp": true,
  "enable_time": true,
  "increment": 1,
  "is_mandatory": false,
  "label": "",
  "link": "",
  "locked": true,
  "max": 4,
  "media": {},
  "min": 2,
  "multiple_selection": false,
  "required": true,
  "response_set": "7bb1cb10-7020-11e2-bcfd-0800200c9a66",
  "failed_responses": ["8bcfbf01-e11b-11e1-9b23-0800200c9a66"],
  "secure": "",
  "type": "media",
  "url": "",
  "values": ["6565F809-B2F9-40AF-909E-2D76BC7683FF"],
  "visible_in_audit": true,
  "visible_in_report": true,
  "weighting": 8,
  "require_note": true,
  "require_media": false,
  "require_action": false
}
Key	Type	Description
condition	String	The smart field condition. UUID of a response set
drawing_base_image	Object	The base image (media) for annotation item
element	String	The title of each element of a dynamic field.
enable_date	Boolean	Toggles the date portion of an item containing a date-time
enable_signature_timestamp	Boolean	Toggles the timestamp set when filling in a signature field
enable_time	Boolean	Toggles the time portion of an item containing a date-time
hide_barcode	Boolean	Means that you can only scan barcode. Not editable.
increment	String	Controls the increment jumps in slider items
is_mandatory	Boolean	Toggles whether the item has to have a response before the inspection can be completed
label	String	The main visual text of an item
link	String	URL field in information items
max	String	Maximum value for a slider item
media	Object	A media attached to the item
min	String	Minimum value for a slider item
multiple_selection	Boolean	True if this field allows multiple selection
response_set	String	A UUID of the response set this item relates to
failed_responses	Array	Array of response IDs that indicate if the item has failed. E.g., for one question the answers “No” and “N/A” should be considered “failed”, but for another question only the “No” is “failed”
secure	Boolean	"Barcode Scanner" - "Visible in Inspection" switch value
type	String	The type of an information field. Currently text, media or link
values	Array	The item's smart field response(s) as an array of strings. They are used to evaluate the smart field condition
visible_in_audit	Boolean	Represents checkbox telling if an information item should be seen by a person conducting the inspection
visible_in_report	Boolean	Represents checkbox telling if an information item should appear in reports
weighting	String	The weight used for generating inspection scores
require_note	Boolean	Only available in smart field items. Represents if a note needs to be provided as part of mandatory evidence for a response
require_media	Boolean	Only available in smart field items. Represents if media needs to be uploaded as part of mandatory evidence for a response
require_action	Boolean	Only available in smart field items. Represents if an action needs to be created as part of the response
Deprecated items that may appear in older inspections but are no longer used

Key	Type	Description
assets	Array	Details about entities (e.g. equipment) to inspect
locked	Boolean	Toggles whether an asset item has been locked
computed_field	String	A older version of a smart field
media_visible_in_report	Boolean	Toggles whether a media item is included in a report
url	String	Use the link URL field in information items instead
Item responses
.items[].responses most of the fields will be absent usually.

JSON

{
  "text": "Flinders St",
  "value": "8",
  "name": "Jon Snow",
  "timestamp": "2015-06-24T02:20:22.000Z",
  "datetime": "2015-06-24T02:01:30.000Z",
  "location_text": "Alligator Creek QLD 4816\nAustralia\n(-19.405835, 146.899124)",
  "location": {},
  "selected": [{}],
  "failed": false,
  "weather": {},
  "media": [{}],
  "image": {}
}
Key	Type	Description
text	String	A simple text the person conducting the inspection types into a text box
value	String	The selected value. Used for sliders, checkboxes and on-off switch
name	String	Someone's name. Used with signature, location and weather items
timestamp	String	Time of an action. Used only with barcode and signature fields
datetime	String	Manually entered date and time. Also used with weather item
location_text	String	Location represented as text (address or coordinates)
location	Object	The location object
selected	Array	The selected responses in questions and multi choice items. Same as template response items
failed	Boolean	Indicates whether the item has failed
weather	Object	Inspection time weather
media	Array	An array of attached photos
image	Object	Signature or drawing. See media
Item scoring
.items[].scoring

JSON

{
  "score": 5,
  "max_score": 10,
  "score_percentage": 50,
  "combined_score": 3,
  "combined_max_score": 12,
  "combined_score_percentage": 25
}
Key	Type	Description
score	Number	Score for the answer
max_score	Number	Maximum possible score for the answer
score_percentage	Number	The percentage value calculated as score/max_score
combined_score	Number	Combined score from all responses if there are multiple
combined_max_score	Number	Combined max score from all responses if there are multiple
combined_score_percentage	Number	The percentage value calculated as combined_score/combined_max_score
Location
JSON

{
  "administrative_area": "QLD",
  "country": "Australia",
  "formatted_address": [
    "Alligator Creek QLD 4816",
    "Australia"
  ],
  "geometry": {
    "coordinates": [
      146.8991244532996,
      -19.40583490239377
    ],
    "type": "Point"
  },
  "iso_country_code": "AU",
  "locality": "Alligator Creek",
  "name": "",
  "postal_code": "4816",
  "sub_administrative_area": "",
  "sub_locality": "Woodstock-Cleveland-Ross",
  "sub_thoroughfare": "",
  "thoroughfare": ""
}
Key	Type	Description
administrative_area	String	
country	String	
formatted_address	Array	Address text, line separated
geometry	Object	The geometry object from GeoJSON specification
iso_country_code	String	
locality	String	
name	String	
postal_code	String	
sub_administrative_area	String	
sub_locality	String	
sub_thoroughfare	String	
thoroughfare	String	
Media
This object is used across the entire inspection JSON.

JSON

{
  "date_created": "2015-03-23T23:57:52.000Z",
  "file_ext": "jpg",
  "media_id": "5f32d80c-3531-457f-b853-5f087927f5b1",
  "label": "can be a file name or any random text",
  "href": "https://api.safetyculture.io/audits/audit_50ba581235704a368d025056a583aa8b/media/5f32d80c-3531-457f-b853-5f087927f5b8"
}
Key	Type	Description
date_created	String	A timestamp of the image or photo
file_ext	String	A file extension representing image type (like png or jpeg)
media_id	String	A unique id of this media file
label	String	A label of the image or photo
href	String	A ready-to-go direct URI to retrieve the file from

Directory (sites and template folders)
The SafetyCulture API gives you access to list, search, create, update, and delete folders.

Each organization can only have up to 50,000 sites.

Each user can only be a member of up to 20 sites. Inherited memberships are not included.

📘 All write paths require the "Platform management: Sites" permission.

Folder (sites) Format
This section describes the complete folder response format.

Note that meta_label is different from custom labels which are used for display purposes only.
Refer to Get custom labels for more information about retrieving and using custom site labels.

Folder
JSON

{
  "folder": {
    "id": "4fb56fa8-fa23-4a9c-907e-8367abc75a2f",
    "name": "221 Sturt st",
    "org_id": "d31e24be-e7a4-4a28-a230-044f850041fc",
    "creator_id": "a3452937-9fa7-4ba2-9ffa-c3bbee3fc947",
    "created_at": "2020-04-28T04:14:31:00Z",
    "modified_at": "2020-04-28T04:14:31:00Z",
    "meta_label": "location"
  }
}
Key	Type	Description
id	String	The folder ID
name	String	The name of the folder
org_id	String	The ID of the creator's organisation
creator_id	String	The ID of the creator
created_at	String	ISO date and time when the folder was created
modified_at	String	ISO date and time when the folder was last modified
meta_label	String	The label of the folder
Folder with member count
JSON

{
  "folder_with_member_count": {
    "folder": {
      "id": "4fb56fa8-fa23-4a9c-907e-8367abc75a2f",
      "name": "221 Sturt st",
      "org_id": "d31e24be-e7a4-4a28-a230-044f850041fc",
      "creator_id": "a3452937-9fa7-4ba2-9ffa-c3bbee3fc947",
      "created_at": "2020-04-28T04:14:31:00Z",
      "modified_at": "2020-04-28T04:14:31:00Z",
      "meta_label": "location"
    },
    "members_count": 5,
    "has_children": false,
    "inherited_member_count": 10,
    "depth": 3,
    "children_count": 0
  }
}
Key	Type	Description
folder	Object	The folder object
member_count	Number	The number of users directly assigned to this folder
has_children	Boolean	Whether or not the folder has any children folders
inherited_member_count	Number	The number of inherited members (members assigned to parent folders)
depth	Number	The depth in the hierarchy starting from 1
children_count	Number	The count of children folders underneath this folder
Folder with ancestors
JSON

{
  "folder_with_ancestors": {
    "folder": {
      "id": "4fb56fa8-fa23-4a9c-907e-8367abc75a2f",
      "name": "221 Sturt st",
      "org_id": "d31e24be-e7a4-4a28-a230-044f850041fc",
      "creator_id": "a3452937-9fa7-4ba2-9ffa-c3bbee3fc947",
      "created_at": "2020-04-28T04:14:31:00Z",
      "modified_at": "2020-04-28T04:14:31:00Z",
      "meta_label": "location"
    },
    "ancestors": [
      {
        "id": "4fb56fa8-fa23-4a9c-907e-8367abc75a2d",
        "name": "Townsville",
        "org_id": "d31e24be-e7a4-4a28-a230-044f850041fc",
        "creator_id": "a3452937-9fa7-4ba2-9ffa-c3bbee3fc947",
        "created_at": "2020-04-28T04:14:31:00Z",
        "modified_at": "2020-04-28T04:14:31:00Z",
        "meta_label": "area"
      },
      {
        "id": "4fb56fa8-fa23-4a9c-907e-8367abc75a2c",
        "name": "Queensland",
        "org_id": "d31e24be-e7a4-4a28-a230-044f850041fc",
        "creator_id": "a3452937-9fa7-4ba2-9ffa-c3bbee3fc947",
        "created_at": "2020-04-28T04:14:31:00Z",
        "modified_at": "2020-04-28T04:14:31:00Z",
        "meta_label": "region"
      }
    ],
    "members_count": 5
  }
}
Key	Type	Description
folder	Array	The folder object
ancestors	Array	An array of parent folder objects (ordered from closest relation to furthest)
members_count	Number	The number of users directly assigned to this folder
Folder with parent
JSON

{
  "folder": {
    "id": "4fb56fa8-fa23-4a9c-907e-8367abc75a2f",
    "name": "221 Sturt st",
    "org_id": "d31e24be-e7a4-4a28-a230-044f850041fc",
    "creator_id": "a3452937-9fa7-4ba2-9ffa-c3bbee3fc947",
    "created_at": "2020-04-28T04:14:31:00Z",
    "modified_at": "2020-04-28T04:14:31:00Z",
    "meta_label": "location"
  },
  "parent_id": "4fb56fa8-fa23-4a9c-907e-8367abc75a2d",
  "depth": 3,
  "member_count": 5
}
Key	Type	Description
folder	Object	The folder object
parent_id	String	The UUID of the parent folder; folders with no parent will use a Nil/Empty UUID
depth	Number	The depth in the hierarchy starting from 1
members_count	Number	The number of users directly assigned to this folder
Folder order by
JSON

{
  "sort_order": 1
}
Key	Type	Description
sort_order	Number	The sort order where 1 is ascending and 2 is descending
Folder filter
Folders can be filtered using an array of meta_label and folder_id filter objects.

If meta-label object(s) and folder-id object(s) are used together, folders will be filtered using an AND operation.
If multiple meta-label objects are used, folder meta-labels will be filtered using an OR operation.
If multiple folder-id objects are used, folder ID's will be filtered using an OR operation.
Examples can be seen here.

meta_label filter object
JSON

{
  "not": false,
  "meta_label": "location"
}
Key	Type	Description
not	Boolean	(required) Whether to include or exclude the filter. {"not": false} would mean include.
meta_label	String	(required) A meta_label to include or exclude from the results; e.g. location
folder_id filter object
JSON

{
  "not": false,
  "folder_id": "4fb56fa8-fa23-4a9c-907e-8367abc75a2d"
}
Key	Type	Description
not	Boolean	(required) Whether to include or exclude the filter. {"not": false} would mean include.
folder_id	String	(required) A meta_label to include or exclude from the results; e.g. 4fb56fa8-fa23-4a9c-907e-8367abc75a2d

Data Feeds
Retrieve all of your SafetyCulture data in a flat format.

General request format
Most of the data feeds contain date and time fields in their output, such as modified_at, modified_after, and modified_before.

When working with date and time in your requests, please ensure you're using the Internet Date-Time format: {year}-{month}-{day}T{hour}:{min}:{sec}[.{frac_sec}]Z. For example, 2014-01-28T23:14:23.000Z.
More information here

General response format
All data feed APIs provide data in the following wrapper format:

JSON

{
  "metadata": {
    "next_page": "/feed/inspections?limit=20&completed=both&archived=both&modified_after=2014-12-06T00%3A37%3A02.837Z",
    "remaining_records": 114642
  },
  "data": [
     {
      "id": "audit_8E2B1F3CB9C94D8792957F9F99E2E4BD",
      "name": "",
      "archived": true,
      "owner_name": "Joe Bloggs",
      "owner_id": "user_38336063a03611e3aaf5001b1118ce11",
      "author_name": "Joe Bloggs",
      "author_id": "user_38336063a03611e3aaf5001b1118ce11",
      "score": null,
      "max_score": 107,
      "score_percentage": null,
      "duration": 61,
      "template_id": "template_3FF54D8127644FE699C2914981E11BEF",
      "template_name": "General Workplace Inspection",
      "template_author": "Anonymous",
      "date_started": "2014-01-28T23:14:23.000Z",
      "date_completed": null,
      "date_modified": "2014-01-28T23:15:24.000Z",
      "created_at": "2014-01-28T23:14:23.000Z",
      "modified_at": "2014-01-28T23:14:23.000Z",
      "document_no": null,
      "prepared_by": null,
      "location": null,
      "conducted_on": "2014-01-28T23:14:23.000Z",
      "personnel": null,
      "client_site": null,
      "web_report_link": "https://app.safetyculture.io/report/audit/audit_8E2B1F3CB9C94D8792957F9F99E2E4BD"
    },
    {},
    {}
  ]
}
The next_page path MUST be used to fetch the next page of data. Do not construct this yourself as it's subject to change and may result in your exports failing in the future.

If next_page returns null, that means there are no more records to fetch.

See the following API usage example:

JavaScript

async fetchInspections() {
  // Only fetch inspections that have been updated
  const lastModifiedAt = await store.getLastModifiedAt('inspections');

  let path = `/feed/inspections?modified_after=${lastModifiedAt.toISOString()}`

  while(url) {
    const response = await get(`https://api.safetyculture.io${path}`);
    await store.saveRows(response.data);

    // next_page will be null when there is no more data to be fetched
    path = response.metadata.next_page;
  }
}

Schedules
The SafetyCulture API gives you access to create, update and delete schedule items.

Schedule item format
List schedule item format
This section describes the complete schedule item response format.

JSON

{
    "id": "87894eeb-ee76-4551-b3ab-0c60c675d820",
    "description": "Workplace Reopening Checklist - Every day",
    "must_complete": "ONE",
    "can_late_submit": true,
    "recurrence": "INTERVAL=1;FREQ=DAILY;DTSTART=20210803T210000Z",
    "start_time": {
        "hour": 9,
        "minute": 0
    },
    "duration": "PT8H",
    "timezone": "Pacific/Auckland",
    "from_date": "2021-08-02T21:00:00Z",
    "to_date": null,
    "reminders": [
        {
            "event": "START",
            "duration": "P0D"
        }
    ],
    "modified_at": "2021-08-10T00:09:50.488Z",
    "created_at": "2021-08-10T00:09:50.488Z",
    "status": "ACTIVE",
    "assignees": [
        {
            "id": "87894eeb-ee76-4551-b3ab-0c60c675d820",
            "type": "ROLE",
            "name": "Joe's Team"
        }
    ],
    "creator": {
        "id": "83224e56-ad58-4e19-b633-fde5271ac8e4",
        "type": "USER",
        "name": "Joe Bloggs"
    },
    "document": {
        "id": "dfa57152-4164-4534-90b4-4992f65630a0",
        "type": "TEMPLATE",
        "name": "Workplace Reopening Checklist"
    },
    "location_id": null,
    "next_occurrence": {
        "start": "2021-08-09T21:00:00Z",
        "due": "2021-08-10T05:00:00Z"
    }
}
Key	Type	Description
id	String	The ID of the schedule item.
description	String	The description of the schedule item.
must_complete	String	Whom must complete a given schedule, either ONE assignee or ALL assignees.
can_late_submit	Boolean	Can the inspections be started after the due date.
recurrence	String (RRule)	RRule formatted recurrence string.
start_time	Object	The time the schedule item starts on each occurrence e.g. {"hour": 15, "minute": 15} for 3:15 PM.
duration	String	ISO8601 duration string, e.g. PT1H. How long inspection can be started after the start_date.
timezone	String	Timezone the schedule item will appear in.
from_date	String (ISO8601)	The starting datetime of the schedule item.
to_date	String (ISO8601)	The end datetime of the schedule item.
reminders	[]Object	The reminders that will be sent to assignees.
modified_at	String (ISO8601)	The datetime when the schedule item was last modified.
created_at	String (ISO8601)	The datetime when the schedule item was created.
status	String	The current status of the schedule item.
assignees	[]Object	The assignees of this schedule item.
creator	Object	The creator of this schedule item.
document	Object	The document/inspection assigned to this schedule item.
location_id	String	The location assigned to this schedule item.
next_occurrence	Object	When this schedule item will next occur.
Update Schedule Item Format
This section describes the complete create/update schedule item format

JSON

{
    "id": "87894eeb-ee76-4551-b3ab-0c60c675d820",
    "description": "Workplace Reopening Checklist - Every day",
    "must_complete": "ONE",
    "can_late_submit": true,
    "recurrence": "INTERVAL=1;FREQ=DAILY;DTSTART=20210803T210000Z",
    "start_time": {
        "hour": 9,
        "minute": 0
    },
    "duration": "PT8H",
    "timezone": "Pacific/Auckland",
    "from_date": "2021-08-02T21:00:00Z",
    "to_date": "2022-08-02T21:00:00Z",
    "reminders": [
        {
            "event": "START",
            "duration": "P0D"
        }
    ],
    "assignees": [
        {
            "id": "87894eeb-ee76-4551-b3ab-0c60c675d820",
            "type": "ROLE"
        }
    ],
    "document": {
        "id": "dfa57152-4164-4534-90b4-4992f65630a0",
        "type": "TEMPLATE"
    },
    "location_id": "dfa57152-4164-4534-90b4-4992f65630a0"
}
Key	Type	Description
description	String	The description of a schedule item.
must_complete	String	Whom must complete a given schedule, either ONE assignee or ALL assignees.
can_late_submit	Boolean	Can the inspections be started after the due date.
recurrence	String (RRule)	RRule formatted recurrence string.
start_time	Object	The time the schedule item starts on each occurrence e.g. {"hour": 15, "minute": 15} for 3:15 PM.
duration	String (ISO8601)	ISO8601 duration string, e.g. PT1H. How long inspection can be started after the start_date.
timezone	String	Timezone the schedule item will appear in.
from_date	String (ISO8601)	The starting datetime of the schedule item.
to_date	String (ISO8601)	The end datetime of the schedule item.
reminders	[]Object	The reminders that will be sent to assignees.
assignees	[]Object	The assignees of this schedule item.
document	Object	The document/inspection assigned to this schedule item.
location_id	String	The new UUID formatted ID of the location assigned to this schedule item.
Schedule Item Entity
Contains information that relates to a user, group or organization.

JSON

{
  "id": "31d302e2-6f49-435f-944e-be8276f284b6",
  "type": "USER",
  "name": "Joe Bloggs"
}
Key	Type	Description
id	String	The new UUID formatted ID of the entity.
type	String	Type of entity either USER or ROLE (group/organization).
name	String	Name of the entity.
Schedule Item Document
Contains information that relates to the document a schedule is assigned to.

JSON

{
  "id": "31d302e2-6f49-435f-944e-be8276f284b6",
  "type": "TEMPLATE",
  "name": "Joe's Daily Site walk through"
}
Key	Type	Description
id	String	The new UUID formatted ID of the document.
type	String	Type of document TEMPLATE is the only accepted option.
name	String	Name of the document.
Schedule Item Reminder
Contains information that relates to a schedule reminder.

JSON

{
  "event": "START",
  "duration": "P0D"
}
Key	Type	Description
event	String	The event that this reminder should be triggered on either START or DUE.
duration	String	ISO8601 duration string, e.g. PT1H. How long before the event to remind the assignees.
Schedule Item Statuses
The current status of a schedule item, the current values are:

Value	Description
ACTIVE	Default value - schedule item is still active.
PAUSED	Schedule has been paused e.g. manually paused/org frozen.
NO_TEMPLATE	The template used for this schedule item has been deleted/archived.
NO_ASSIGNEE	No valid assignees exist for this schedule item anymore.
FINISHED	The schedule item has hit its end date or count limit and is now complete.

ctions
The SafetyCulture API gives you direct access to your Actions data. There are methods to search and retrieve actions.

Action format
This section describes the complete action response format.

Action top level
JSON

{
  "action": {
    "task": {
      "task_id": "d6658a5a-6154-4802-b1f3-953a67e492c6",
      "creator": {
        "user_id": "c3aa4fae-bbad-4abf-8550-29c683012796",
        "firstname": "SafetyCulture",
        "lastname": "User"
      },
      "title": "Test Action",
      "description": "This is a test action generated by the SafetyCulture API.",
      "created_at": "2022-02-21T23:59:00.226559Z",
      "due_at": null,
      "priority_id": "58941717-817f-4c7c-a6f6-5cd05e2bbfde",
      "status_id": "17e793a1-26a3-4ecd-99ca-f38ecc6eaa2e",
      "collaborators": [],
      "template_id": "",
      "inspection": {
        "inspection_id": "",
        "inspection_name": ""
      },
      "inspection_item": {
        "inspection_item_id": "",
        "inspection_item_name": "",
        "inspection_item_type": "",
        "inspection_item_response_values": []
      },
      "site": {
        "id": "",
        "name": "",
        "region": "",
        "area": ""
      },
      "modified_at": "2022-02-21T23:59:00.226559Z",
      "references": [],
      "completed_at": null,
      "template_name": "",
      "status": {
        "status_id": "17e793a1-26a3-4ecd-99ca-f38ecc6eaa2e",
        "key": "TO_DO",
        "label": "To Do",
        "display_order": 1
      }
    }
  }
}
Key	Type	Description
task_id	String (UUID)	The action ID.
template_id	String (UUID)	The template ID of the inspection which the action belongs to.
template_name	String	The template name of the inspection which the action belongs to.
inspection	Object	The inspection which the action belongs to inspection.
inspection_item	Object	The inspection item which the action belongs to inspection_item.
creator	Object	Information about the action creator.
title	String	The title of the action.
description	String	The description of the action.
created_at	String (ISO8601)	Date and time when the action was created.
modified_at	String (ISO8601)	Date and time when the action was last modified.
completed_at	String (ISO8601)	Date and time when the action was completed.
due_at	String (ISO8601)	Date and time when the action is due.
priority_id	String (UUID)	ID of the action priority.
status	Object	Status information of the action status.
site	Object	General information of the site where the action was created.
collaborators	Array	List of Collaborators of the action.
reference	Object	Information about from where the action was created. Only available when the action was created from an Inspection or a Sensor Alert.
Inspection
.inspection contains the information about the inspection which action belongs to.

JSON

{
  "inspection": {
    "inspection_id": "40a57fda-bb93-4891-9db3-d34466adeedd",
    "inspection_name": "25 Nov 2021 / Safetyculture user"
  }
}
Key	Type	Description
inspection_id	String (UUID)	ID of the inspection.
inspection_name	String	name of the inspection.
Inspection item
.inspection_item contains the information about the inspection item which action belongs to.

JSON

{
  "inspection_item": {
    "inspection_item_id": "09ce922d-a3c4-426b-8860-27adfcb5e89f",
    "inspection_item_name": "question name",
    "inspection_item_type": "question"
  }
}
Key	Type	Description
inspection_item_id	String (UUID)	ID of the inspection item.
inspection_item_name	String	name of the inspection item.
inspection_item_type	String	type of the inspection item.
Creator
.creator contains the information about the creator of the action.

JSON

{
  "creator": {
    "user_id": "c3aa4fae-bbad-4abf-8550-29c683012796",
    "firstname": "SafetyCulture",
    "lastname": "User"
  }
}
Key	Type	Description
id	String (UUID)	ID of the creator of the action.
firstname	String	First name of the creator of the action.
lastname	String	Last name of the creator of the action.
Action site
.site contains the information about the site which the action belongs to.

JSON

{
  "site": {
    "id": "704d6061-0383-4e2c-a8dc-a1804712677a",
    "name": "Bilpin",
    "region": "NSW",
    "area": "Australia"
  }
}
Key	Type	Description
id	String (UUID)	ID of the site.
name	String	Name of the site.
region	String	The region of the site.
area	String	The area of the site.
Priority
.priority_id contains the id of the priority of an action.

The current accepted priorities are:

ID	Value
58941717-817f-4c7c-a6f6-5cd05e2bbfde	None
16ba4717-adc9-4d48-bf7c-044cfe0d2727	Low
ce87c58a-eeb2-4fde-9dc4-c6e85f1f4055	Medium
02eb40c1-4f46-40c5-be16-d32941c96ec9	High
Status
.status contains the information about the status of an action.

JSON

{
  "status": {
    "status_id": "17e793a1-26a3-4ecd-99ca-f38ecc6eaa2e",
    "key": "TO_DO",
    "label": "To Do",
    "display_order": 1
  }
}
Key	Type	Description
status_id	String (UUID)	ID of the status.
label	String	Name of the status.
Action status labels can be customized for an organization. If an action status's label is not customized, it should be using one of the following default labels:

ID	Label	Action is completed?
17e793a1-26a3-4ecd-99ca-f38ecc6eaa2e	To do	No
20ce0cb1-387a-47d4-8c34-bc6fd3be0e27	In progress	No
7223d809-553e-4714-a038-62dc98f3fbf3	Complete	Yes
06308884-41c2-4ee0-9da7-5676647d3d75	Can't do	Yes
Collaborators
.collaborators contains the information about the collaborators of the action. It can contain multiple users, groups or external users.

JSON

{
  "collaborators": [
    {
      "collaborator_id": "c3aa4fae-bbad-4abf-8550-29c683012796",
      "collaborator_type": "USER",
      "assigned_role": "ASSIGNEE",
      "user": {
        "user_id": "c3aa4fae-bbad-4abf-8550-29c683012796",
        "firstname": "SafetyCulture",
        "lastname": "User"
      }
    },
    {
      "collaborator_id": "f877808b-9b86-4147-9269-274e0169e021",
      "collaborator_type": "GROUP",
      "assigned_role": "ASSIGNEE",
      "group": {
        "group_id": "f877808b-9b86-4147-9269-274e0169e021",
        "name": "Test Group"
      }
    },
    {
      "collaborator_id": "4251c7c8-9af6-4233-8d4e-967b28a48c93",
      "collaborator_type": "EXTERNAL_USER",
      "assigned_role": "ASSIGNEE",
      "external_user": {
        "id": "4251c7c8-9af6-4233-8d4e-967b28a48c93",
        "email": "external.user@safetyculture.io"
      }
    }
  ]
}
Collaborator data
Key	Type	Description
collaborator_id	String (UUID)	ID of the collaborator of the action.
collaborator_type	String	The type of collaborator of the action.
assigned_role	String	The role of collaborator of the action.
user	Object	Information about the user. Only available when the collaborator_type is COLLABORATOR_TYPE_USER.
group	Object	Information about the group. Only available when the collaborator_type is COLLABORATOR_TYPE_GROUP.
external_user	Object	Information about the external user. Only available when the collaborator_type is COLLABORATOR_TYPE_EXTERNAL_USER.
Collaborator type
The type of the collaborator.

Key	Description
USER	The collaborator is a specific user.
GROUP	The collaborator is a group. This means that every user that belongs to that group is also a collaborator.
EXTERNAL_USER	The collaborator is not a SafetyCulture user.
Collaborator role
The current role of an action collaborator.

Key	Description
ASSIGNEE	The collaborator is an assignee of the action.
User
.collaborators[].user contains the information about a specific user.

JSON

{
  "user": {
    "user_id": "c3aa4fae-bbad-4abf-8550-29c683012796",
    "firstname": "SafetyCulture",
    "lastname": "User"
  }
}
Key	Type	Description
user_id	String (UUID)	ID of the user.
firstname	String	First name of the user.
lastname	String	Last name of the user.
Group
.collaborators[].group contains the information about a group.

JSON

{
  "group": {
    "group_id": "f877808b-9b86-4147-9269-274e0169e021",
    "name": "Test Group"
  }
}
Key	Type	Description
group_id	String (UUID)	ID of the group.
name	String	Name of the group.
External user
.collaborators[].external_user contains the information about an external user (an user who do not belong to the organisation).

JSON

{
  "external_user": {
    "id": "4251c7c8-9af6-4233-8d4e-967b28a48c93",
    "email": "external.user@safetyculture.io"
  }
}
Key	Type	Description
id	String (UUID)	ID of the external user.
email	String	Email of the external user.
Reference
.reference contains information about the entity that originated the action. Not available for standalone actions.

JSON

{
  "reference": {
    "type": "INSPECTION",
    "id": "51d4482f-f78b-5a30-9618-2217025f55cc",
    "inspection_context": {},
    "sensor_alert_context": {}
  }
}
Key	Type	Description
type	String	Type of the reference.
id	String (UUID)	ID of the referenced entity.
inspection_context	Object	Information about the Inspection that originated the action. Only available when the action was created from an Inspection.
sensor_alert_context	Object	Information about the Sensor Alert that originated the action. Only available when the action was created from a Sensor Alert.
Reference type
.reference.type contains the type of the entity that originated the action.

Type	Description
INSPECTION	Indicates that the action was created from an inspection or inspection item. When the reference is from this type, the reference.id will be the ID of the Inspection.
SENSOR_ALERT	Indicates that the action was created from a sensor alert. When the reference is from this type, the reference.id will be the ID of the Sensor Alert.
Inspection context
.reference.inspection_context contains the information of the inspection and inspection item that originated the action.

JSON

{
  "inspection_context": {
    "inspection_id": "effa93bb-8cfb-4783-af5d-c507340dc6e0",
    "inspection_name": "11 Aug 2021 / Checklist",
    "inspection_item_id": "67034555-c11e-4411-bf75-140866c555be",
    "inspection_item_name": "Question Name",
    "inspection_item_type": "",
    "inspection_item_path": []
  }
}
Key	Type	Description
inspection_id	String (UUID)	ID of the inspection (UUID).
inspection_name	String	Name of the inspection.
inspection_item_id	String (UUID)	ID of the inspection item (UUID).
inspection_item_name	String	Name of the inspection item.
inspection_item_type	String	Name of the inspection item type.
inspection_item_path	String	The ancestor Names of the inspection item.
Sensor alert context
.reference.sensor_alert_context contains the information of the sensor alert that originated the action.

JSON

{
  "sensor_alert_context": {
    "sensor_alert_id": "79ce7380-0809-5a0a-9d58-a7ead30d078e",
    "level": "OK",
    "created_at": "2021-12-01T12:39:09.313635Z",
    "detected_at": "2021-11-30T22:55:00Z",
    "sensor_id": "a5ea5ae1-304c-46ef-9dfd-ce845208290f",
    "site_name": "2 Lacey St - L1",
    "metric_type": "WIND_GUST",
    "sensor_name": "Weather"
  }
}
Key	Type	Description
sensor_alert_id	String (UUID)	ID of the sensor alert.
level	String	Level of importance of the sensor alert.
created_at	String (ISO8601)	Date and time when the alert was created.
detected_at	String (ISO8601)	Date and time when the alert was detected.
sensor_id	String (UUID)	ID of the sensor where the alert was created.
site_name	String	Name of the site where the alert was created.
metric_type	String	Type of the alert metric.
sensor_name	String	Name of the sensor where the alert was created.
Sensor alert event level
.reference.sensor_alert_context.level represents the level of importance of the sensor alert.

Level	Description
ALERT_EVENT_LEVEL_OK	Indicates that the device metric becomes healthy.
ALERT_EVENT_LEVEL_INFO	Indicates that the first alert was sent.
ALERT_EVENT_LEVEL_WARN	Indicates that the second alert was sent.
ALERT_EVENT_LEVEL_CRITICAL	Indicates that the third alert was sent.
Sensor alert metric type
.reference.sensor_alert_context.metric_type represents the type of received metric.

Type	Description
METRIC_TYPE_TEMPERATURE	Temperature metric.
METRIC_TYPE_HUMIDITY	Humidity metric.
METRIC_TYPE_BATTERY	Battery level. Percentage based i.e. 0 - 100.
METRIC_TYPE_SIGNAL	Signal strength metric.
METRIC_TYPE_AIR_QUALITY_PM25	Air quality for particulate matter less than 2.5 microns.
METRIC_TYPE_AIR_QUALITY_PM10	Air quality for particulate matter less than 10 microns.
METRIC_TYPE_TEMPERATURE_2	Alternative temperature for hardware that sends 2 temperatures.
METRIC_TYPE_DIFFERENTIAL_AIR_PRESSURE	Differential air pressure.
METRIC_TYPE_CO	Carbon monoxide.
METRIC_TYPE_DOOR_OPEN_CLOSED	Door open/closed (boolean metric).
METRIC_TYPE_BATTERY_VOLTAGE	Battery voltage metric.

Issues
The SafetyCulture API gives you access to your Issues data. The API includes methods to retrieve a list of issues, retrieve a specific issue, as well as endpoints to create and update an issue. Issues has some methods of access control, such as site-based access and category level restrictions. However, if the account being used for API access has the "Manage all data" permission, this permission will act as an override and give access to all data within your organisation.

Note that much of the Issues API has references to "incident", including the endpoints and the response objects. Issues used to be called Incidents, but was renamed. For all intents and purposes, "incident" is synonymous with "issue".

Issue format
This section describes the complete issue response format.

JSON

{
  "incident": {
    "task": {
      "task_id": "eaf9b051-914e-4ca3-8571-e6e8e816ec3c",
      "creator": {},
      "title": "Test Issue",
      "description": "This is a test issue generated by the SafetyCulture API.",
      "created_at": "2022-01-25T05:42:21.832670Z",
      "due_at": "2022-01-27T05:42:21.832670Z",
      "priority_id": "58941717-817f-4c7c-a6f6-5cd05e2bbfde",
      "status_id": "547ed646-5e34-4732-bb54-a199d304368a",
      "collaborators": [],
      "template_id": "",
      "inspection": {},
      "inspection_item": {},
      "site": {},
      "occurred_at": "2022-01-25T05:42:21.832670Z",
      "modified_at": "2022-02-03T00:48:59.689138Z",
      "references": [],
      "completed_at": null,
      "template_name": "",
      "status": null
    },
    "category_id": "01cc874c-a6c8-464b-ae75-ab8688f1113c",
    "category": {},
    "media": [],
    "location": null,
    "inspections": []
  }
}
Creator
.creator contains the information about the creator of the issue.

JSON

{
  "creator": {
    "user_id": "04b11270-14f8-4f46-81e6-6694fee2ee19",
    "firstname": "SafetyCulture",
    "lastname": "User"
  },
}
Key	Type	Description
id	String (UUID)	ID of the creator of the action.
firstname	String	First name of the creator of the action.
lastname	String	Last name of the creator of the action.
Collaborators
.collaborators contains the information about the assignee of the issue.

JSON

{
  "collaborators": [
    {
      "collaborator_id": "eb6307fb-cf76-402b-b64a-8e61f8959ce8",
      "collaborator_type": "USER",
      "assigned_role": "ASSIGNEE",
      "user": {
        "user_id": "eb6307fb-cf76-402b-b64a-8e61f8959ce8",
        "firstname": "SafetyCulture",
        "lastname": "User"
      }
    }
  ]
}
Key	Type	Description
assigned_role	String	The role of the assignee of the issue. Will only be ASSIGNEE.
collaborator_type	String	The type of assignee of the issue. Will only be USER.
user	Object	Information about the user.
Key	Type	Description
user_id	String (UUID)	The ID of the user who is assigned to the issue.
firstname	String	The first name of the user who is assigned to the issue.
lastname	String	The last name of the user who is assigned to the issue.
Inspections
The fields, .inspection and .inspection_item are deprecated. Inspections that have been linked to an issue are in .inspections.

JSON

{
  "inspections": [
    {
      "id": "c29994d6-f581-4a50-bcc7-9df75bf07918",
      "created_at": "2022-01-31T06:01:54.238Z",
      "status": "INSPECTION_STATUS_DELETED",
      "title": "31 Jan 2022 / SafetyCulture User",
      "template_title": "Test template"
    }
  ]
}
Key	Type	Description
id	String	The ID of the inspection.
created_at	Timestamp	The time that the inspection was created.
status	String	The current status of the linked inspection. The values will be either INSPECTION_STATUS_IN_PROGRESS to indicate the inspection is in progress, INSPECTION_STATUS_COMPLETED to indicate that the inspection has been completed, or INSPECTION_STATUS_DELETED to indicate that the inspection has been deleted.
title	String	The title of the inspection.
template_title	String	The title of the template that this inspection was created from.
Site
.site contains information about the site that the issue occurred at.

JSON

{
  "site": {
    "id": "704d6061-0383-4e2c-a8dc-a1804712677a",
    "name": "Bilpin",
    "region": "NSW",
    "area": "Australia"
  },
}
Key	Type	Description
id	String (UUID)	The ID of the site.
name	String	The name of the site.
region	String	The region of the site.
area	String	The area of the site.
Category
A category is used to classify an issue. For example, you can filter issues by category for analytics, or give users or groups access to issues from a category.

JSON

{
  "category": {
    "id": "01cc874c-a6c8-464b-ae75-ab8688f1113c",
    "key": "Maintenance",
    "label": "Maintenance",
    "description": "",
    "display_order": 0,
    "is_visible": true,
    "use_category_access_whitelist": false
  }

}
Key	Type	Label	Description
id	String (UUID)	The UUID of a category.	
key	String	The name of a category. This can be a default name or one that is customized in your organization.	
label	String	The name of a category. This field's value is the same as the value for key.	
description	String	The description of a category. This is unused, and is hardcoded to an empty string, ``.	
display_order	int32	The sorting order of a list of categories. This is unused, and is hardcoded as 0.	
is_visible	Boolean	The indicator for whether a category is visible or not for an organization on the web app and the mobile app.	
use_category_access_whitelist	Boolean	The indicator for whether a category's issues can be accessed by anyone in your organization or not. If this is false for a category, then that category's issues can only be accessed by creators and assignees.	
Media
The media attached to an issue. This can be either an image, PDF or a video.

JSON


{
  "media": {
    "id": "17fe46fd-93ef-49c9-8b90-a87f682a85d6",
    "token": "2702fbfa8a6b8b1eba08c9481b137951cdc3be2acd4fffa4df76e9fbcbbd3dee",
    "filename": "0e96f162-7ba3-4221-acd9-dc45ea33bf04.jpg",
    "media_type": "MEDIA_TYPE_IMAGE"
  },
}
Key	Type	Description	
id	String (UUID)	The ID of this media item.	
token	String	A unique identifier for this media item.	
filename	String	The filename for this media item.	
media_type	String	The type of this media item. This will be MEDIA_TYPE_IMAGE for an image, MEDIA_TYPE_VIDEO for a video, or MEDIA_TYPE_PDF for a PDF.	
Issue location
The location of the issue.

JSON

{
  "location": {
    "name": "42 Wallaby Way, Sydney NSW 2037, Australia",
    "thoroughfare": "Wallaby Way",
    "sub_thoroughfare": "42",
    "locality": "Sydney",
    "sub_locality": "Sydney",
    "administrative_area": "NSW",
    "sub_administrative_area": "Sydney",
    "postal_code": "2000",
    "country": "Australia",
    "iso_country_code": "AU",
    "geo_position": {
      "longitude": 151.2107,
      "latitude": -33.8521,
      "accuracy": 0
    }
  }
}
Key	Type	Description
name	String	The name of the issue's location.
thoroughfare	String	The thoroughfare of the location.
sub_thoroughfare	String	The sub-thoroughfare of the location.
locality	String	The locality of the location.
sub_locality	String	The sub_locality of the location.
administrative_area	String	The administrative area of the location.
sub_administrative_area	String	The sub-administrative area of the location.
postal_code	String	The postal_code of the location.
country	String	The country of the location.
iso_country_code	String	The ISO country code of the location.
geo_position	Object	The geoposition of the location.
Geoposition
A geoposition is an object containing the latitude and longitude.

JSON

{
  "geo_position": {
    "latitude": -33.8521,
    "longitude": 151.2107,
    "accuracy": 10,
  }
}
Key	Type	Description	
longitude	double	The longitude of the location.	
latitude	double	The latitude of the location.	
accuracy	int32	The accuracy of the location.	
Reference
.reference contains information about an entity that originated from an issue.

JSON

{
  "reference": {
    "type": "ACTION",
    "id": "51d4482f-f78b-5a30-9618-2217025f55cc",
    "action_context": {},
  }
}
Key	Type	Description
type	String	The type of a reference.
id	String (UUID)	The unique identifier of a referenced entity.
action_context	Object	The information about an action that originated from an issue.

Search modified templates
get
https://api.safetyculture.io/templates/search
The template search endpoint allows you to retrieve the template ID, name, modification date and creation date, of
templates that meet a certain criteria. It is possible to request templates modified between given dates, and whether
or not to include archived templates.

In the request, you must specify the fields that you want to return. The field template_id is not required, the template ID will be always included in every template result returned in the response.
To include other template properties in the response you can optionally add parameters modified_at, created_at and name. Multiple field elements can be provided.

Dates must be formatted according to ISO 8601 date and time format. For example,
2015-04-01T00:00:00.000Z or 2015-04-01T00:00+1000.

🚧
The modification dates used for searching are related to SafetyCulture's cloud storage and include latest sync times, modifications through the SafetyCulture website, and other system modifications. This means that the date may not match the last date that the template was modified. This will ensure that you may consistently find all of the template modified since your last search, even if they are synced some time after they are last changed.

import requests

url = "https://api.safetyculture.io/templates/search?order=asc&archived=false&owner=all"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)

Get template (by inspection)
get
https://api.safetyculture.io/templates/v1/templates/inspections/{inspection_id}
Path Params
inspection_id
string
required
The ID for the inspection.

Query Params
locale
string
The preferred locale of the template.

Responses

200
A successful response.


default
An unexpected error response.

Response body
object
code
int32
message
string
details
array of objects
object
@type
string
A URL/resource name that uniquely identifies the type of the serialized
protocol buffer message. This string must contain at least
one "/" character. The last segment of the URL's path must represent
the fully qualified name of the type (as in
path/google.protobuf.Duration). The name should be in a canonical form
(e.g., leading "." is not accepted).

In practice, teams usually precompile into the binary all types that they
expect it to use in the context of Any. However, for URLs which use the
scheme http, https, or no scheme, one can optionally set up a type
server that maps type URLs to message definitions as follows:

If no scheme is provided, https is assumed.
An HTTP GET on the URL must yield a [google.protobuf.Type][]
value in binary format, or produce an error.
Applications are allowed to cache lookup results based on the
URL, or have them precompiled into a binary to avoid any
lookup. Therefore, binary compatibility needs to be preserved
on changes to types. (Use versioned type names to manage
breaking changes.)
Note: this functionality is not currently available in the official
protobuf release, and it is not used for type URLs beginning with
type.googleapis.com.

Schemes other than http, https (or the empty scheme) might be
used with implementation specific semantics.


View Additional Properties

import requests

url = "https://api.safetyculture.io/templates/v1/templates/inspections/inspection_id"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)

