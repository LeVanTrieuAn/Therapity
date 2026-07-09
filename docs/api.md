[users]()

**GET**[/users:list]()

#### Parameters

Try it out

No parameters

#### Responses

| Code | Description                                                                    | Links |
| ---- | ------------------------------------------------------------------------------ | ----- |
| 200  | okMedia typeapplication/jsonControls `Accept` header.* Example Value* Schema |       |

```json
[
  {
"id": 0,
"displayname": "string",
"username": "string",
"email": "string",
"phone": "string",
"password": "string",
"createdAt": "2026-06-03T02:41:19.712Z",
"updatedAt": "2026-06-03T02:41:19.712Z"
  }
]
```

 | *No links* |

**GET**[/users:get]()

#### Parameters

Try it out

| Name                             | Description |
| -------------------------------- | ----------- |
| filterByTargetKey*integer(query) | user id[ ]  |

#### Responses

| Code | Description                                                                    | Links |
| ---- | ------------------------------------------------------------------------------ | ----- |
| 200  | okMedia typeapplication/jsonControls `Accept` header.* Example Value* Schema |       |

```json
{
"id": 0,
"displayname": "string",
"username": "string",
"email": "string",
"phone": "string",
"password": "string",
"createdAt": "2026-06-03T02:41:19.715Z",
"updatedAt": "2026-06-03T02:41:19.715Z"
}
```

 | *No links* |

**POST**[/users:create]()

#### Parameters

Try it out

No parameters

#### Request body

application/json

* Example Value
* Schema

```json
{
"id": 0,
"displayname": "string",
"username": "string",
"email": "string",
"phone": "string",
"password": "string",
"createdAt": "2026-06-03T02:41:19.719Z",
"updatedAt": "2026-06-03T02:41:19.719Z"
}
```

#### Responses

| Code | Description                                                                    | Links |
| ---- | ------------------------------------------------------------------------------ | ----- |
| 200  | OKMedia typeapplication/jsonControls `Accept` header.* Example Value* Schema |       |

```json
{
"id": 0,
"displayname": "string",
"username": "string",
"email": "string",
"phone": "string",
"password": "string",
"createdAt": "2026-06-03T02:41:19.722Z",
"updatedAt": "2026-06-03T02:41:19.722Z"
}
```

 | *No links* |

**POST**[/users:update]()

#### Parameters

Try it out

| Name                             | Description |
| -------------------------------- | ----------- |
| filterByTargetKey*integer(query) | user id[ ]  |

#### Request body

application/json

* Example Value
* Schema

```json
{
"id": 0,
"displayname": "string",
"username": "string",
"email": "string",
"phone": "string",
"password": "string",
"createdAt": "2026-06-03T02:41:19.725Z",
"updatedAt": "2026-06-03T02:41:19.725Z"
}
```

#### Responses

| Code | Description                                                                    | Links |
| ---- | ------------------------------------------------------------------------------ | ----- |
| 200  | okMedia typeapplication/jsonControls `Accept` header.* Example Value* Schema |       |

```json
{
"id": 0,
"displayname": "string",
"username": "string",
"email": "string",
"phone": "string",
"password": "string",
"createdAt": "2026-06-03T02:41:19.728Z",
"updatedAt": "2026-06-03T02:41:19.728Z"
}
```

 | *No links* |

**POST**[/users:destroy]()

#### Parameters

Try it out

| Name                            | Description  |
| ------------------------------- | ------------ |
| filterByTargetKey*string(query) | role name[ ] |

#### Responses

| Code | Description | Links        |
| ---- | ----------- | ------------ |
| 200  | OK          | *No links* |

### [chat_sessions]()Chat Sessions

**GET**[/chat_sessions:list]()Returns a list of the collection

**GET**[/chat_sessions:get]()Return a record

**POST**[/chat_sessions:create]()Create record

**POST**[/chat_sessions:update]()Update record

**POST**[/chat_sessions:destroy]()Delete record

### [chat_sessions.relation_chat_sessions_users]()Many to one relationship, Chat Sessions/Relation Chat Sessions Users

**GET**[/chat_sessions/{collectionIndex}/relation_chat_sessions_users:get]()Return a record of Many to one

**POST**[/chat_sessions/{collectionIndex}/relation_chat_sessions_users:set]()Associate a record

**POST**[/chat_sessions/{collectionIndex}/relation_chat_sessions_users:remove]()Disassociate the relationship record

**POST**[/chat_sessions/{collectionIndex}/relation_chat_sessions_users:update]()Update the relationship record

**POST**[/chat_sessions/{collectionIndex}/relation_chat_sessions_users:create]()Create and associate a record

**POST**[/chat_sessions/{collectionIndex}/relation_chat_sessions_users:destroy]()Destroy and disassociate the relationship record


### [tasks]()Tasks

**GET**[/tasks:list]()Returns a list of the collection

**GET**[/tasks:get]()Return a record

**POST**[/tasks:create]()Create record

**POST**[/tasks:update]()Update record

**POST**[/tasks:destroy]()Delete record

### [tasks.Relation_Tasks_Users]()Many to one relationship, Tasks/Relation Tasks Users

**GET**[/tasks/{collectionIndex}/Relation_Tasks_Users:get]()Return a record of Many to one

**POST**[/tasks/{collectionIndex}/Relation_Tasks_Users:set]()Associate a record

**POST**[/tasks/{collectionIndex}/Relation_Tasks_Users:remove]()Disassociate the relationship record

**POST**[/tasks/{collectionIndex}/Relation_Tasks_Users:update]()Update the relationship record

**POST**[/tasks/{collectionIndex}/Relation_Tasks_Users:create]()Create and associate a record

**POST**[/tasks/{collectionIndex}/Relation_Tasks_Users:destroy]()Destroy and disassociate the relationship record


### [aoa_comments]()AOA Comments

**GET**[/aoa_comments:list]()Returns a list of the collection

**GET**[/aoa_comments:get]()Return a record

**POST**[/aoa_comments:create]()Create record

**POST**[/aoa_comments:update]()Update record

**POST**[/aoa_comments:destroy]()Delete record

### [aoa_comments.Relation_AOA_Users]()Many to one relationship, AOA Comments/Relation AOA Users

**GET**[/aoa_comments/{collectionIndex}/Relation_AOA_Users:get]()Return a record of Many to one

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Users:set]()Associate a record

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Users:remove]()Disassociate the relationship record

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Users:update]()Update the relationship record

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Users:create]()Create and associate a record

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Users:destroy]()Destroy and disassociate the relationship record

### [aoa_comments.Relation_AOA_Comments_Post]()Many to one relationship, AOA Comments/Relation AOA Comments Post

**GET**[/aoa_comments/{collectionIndex}/Relation_AOA_Comments_Post:get]()Return a record of Many to one

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Comments_Post:set]()Associate a record

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Comments_Post:remove]()Disassociate the relationship record

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Comments_Post:update]()Update the relationship record

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Comments_Post:create]()Create and associate a record

**POST**[/aoa_comments/{collectionIndex}/Relation_AOA_Comments_Post:destroy]()Destroy and disassociate the relationship record


### [aoa_posts]()AOA Posts

**GET**[/aoa_posts:list]()Returns a list of the collection

**GET**[/aoa_posts:get]()Return a record

**POST**[/aoa_posts:create]()Create record

**POST**[/aoa_posts:update]()Update record

**POST**[/aoa_posts:destroy]()Delete record

### [aoa_posts.Relation_Post_User]()Many to one relationship, AOA Posts/Relation Post User

**GET**[/aoa_posts/{collectionIndex}/Relation_Post_User:get]()Return a record of Many to one

**POST**[/aoa_posts/{collectionIndex}/Relation_Post_User:set]()Associate a record

**POST**[/aoa_posts/{collectionIndex}/Relation_Post_User:remove]()Disassociate the relationship record

**POST**[/aoa_posts/{collectionIndex}/Relation_Post_User:update]()Update the relationship record

**POST**[/aoa_posts/{collectionIndex}/Relation_Post_User:create]()Create and associate a record

**POST**[/aoa_posts/{collectionIndex}/Relation_Post_User:destroy]()Destroy and disassociate the relationship record


### [roadmap_tasks]()Roadmap Tasks

**GET**[/roadmap_tasks:list]()Returns a list of the collection

**GET**[/roadmap_tasks:get]()Return a record

**POST**[/roadmap_tasks:create]()Create record

**POST**[/roadmap_tasks:update]()Update record

**POST**[/roadmap_tasks:destroy]()Delete record

### [roadmap_tasks.Relation_Task_Roadmap]()Many to one relationship, Roadmap Tasks/Relation Task Roadmap

**GET**[/roadmap_tasks/{collectionIndex}/Relation_Task_Roadmap:get]()Return a record of Many to one

**POST**[/roadmap_tasks/{collectionIndex}/Relation_Task_Roadmap:set]()Associate a record

**POST**[/roadmap_tasks/{collectionIndex}/Relation_Task_Roadmap:remove]()Disassociate the relationship record

**POST**[/roadmap_tasks/{collectionIndex}/Relation_Task_Roadmap:update]()Update the relationship record

**POST**[/roadmap_tasks/{collectionIndex}/Relation_Task_Roadmap:create]()Create and associate a record

**POST**[/roadmap_tasks/{collectionIndex}/Relation_Task_Roadmap:destroy]()Destroy and disassociate the relationship record


### [diary_folders]()Diary Folders

**GET**[/diary_folders:list]()Returns a list of the collection

**GET**[/diary_folders:get]()Return a record

**POST**[/diary_folders:create]()Create record

**POST**[/diary_folders:update]()Update record

**POST**[/diary_folders:destroy]()Delete record

### [diary_folders.Relation_Diary_Folders_User]()Many to one relationship, Diary Folders/Relation Diary Folders User

**GET**[/diary_folders/{collectionIndex}/Relation_Diary_Folders_User:get]()Return a record of Many to one

**POST**[/diary_folders/{collectionIndex}/Relation_Diary_Folders_User:set]()Associate a record

**POST**[/diary_folders/{collectionIndex}/Relation_Diary_Folders_User:remove]()Disassociate the relationship record

**POST**[/diary_folders/{collectionIndex}/Relation_Diary_Folders_User:update]()Update the relationship record

**POST**[/diary_folders/{collectionIndex}/Relation_Diary_Folders_User:create]()Create and associate a record

**POST**[/diary_folders/{collectionIndex}/Relation_Diary_Folders_User:destroy]()Destroy and disassociate the relationship record


### [diary_entries]()Diary Entries

**GET**[/diary_entries:list]()Returns a list of the collection

**GET**[/diary_entries:get]()Return a record

**POST**[/diary_entries:create]()Create record

**POST**[/diary_entries:update]()Update record

**POST**[/diary_entries:destroy]()Delete record

### [diary_entries.Relation_Diary_Entries_Users]()Many to one relationship, Diary Entries/Relation Diary Entries Users

**GET**[/diary_entries/{collectionIndex}/Relation_Diary_Entries_Users:get]()Return a record of Many to one

**POST**[/diary_entries/{collectionIndex}/Relation_Diary_Entries_Users:set]()Associate a record

**POST**[/diary_entries/{collectionIndex}/Relation_Diary_Entries_Users:remove]()Disassociate the relationship record

**POST**[/diary_entries/{collectionIndex}/Relation_Diary_Entries_Users:update]()Update the relationship record

**POST**[/diary_entries/{collectionIndex}/Relation_Diary_Entries_Users:create]()Create and associate a record

**POST**[/diary_entries/{collectionIndex}/Relation_Diary_Entries_Users:destroy]()Destroy and disassociate the relationship record


### [personal_roadmaps]()Personal Roadmaps

**GET**[/personal_roadmaps:list]()Returns a list of the collection

**GET**[/personal_roadmaps:get]()Return a record

**POST**[/personal_roadmaps:create]()Create record

**POST**[/personal_roadmaps:update]()Update record

**POST**[/personal_roadmaps:destroy]()Delete record

### [personal_roadmaps.relation_roadmaps_user]()Many to one relationship, Personal Roadmaps/Relation Roadmaps User

**GET**[/personal_roadmaps/{collectionIndex}/relation_roadmaps_user:get]()Return a record of Many to one

**POST**[/personal_roadmaps/{collectionIndex}/relation_roadmaps_user:set]()Associate a record

**POST**[/personal_roadmaps/{collectionIndex}/relation_roadmaps_user:remove]()Disassociate the relationship record

**POST**[/personal_roadmaps/{collectionIndex}/relation_roadmaps_user:update]()Update the relationship record

**POST**[/personal_roadmaps/{collectionIndex}/relation_roadmaps_user:create]()Create and associate a record

**POST**[/personal_roadmaps/{collectionIndex}/relation_roadmaps_user:destroy]()Destroy and disassociate the relationship record

### [personal_roadmaps.fk_roadmap_task]()One to many relationship, Personal Roadmaps/Roadmap Tasks

**GET**[/personal_roadmaps/{collectionIndex}/fk_roadmap_task:list]()Return a list of One to many relationship

**GET**[/personal_roadmaps/{collectionIndex}/fk_roadmap_task:get]()Return a record of One to many

**POST**[/personal_roadmaps/{collectionIndex}/fk_roadmap_task:create]()Create and associate a record

**POST**[/personal_roadmaps/{collectionIndex}/fk_roadmap_task:update]()Update the relationship record

**POST**[/personal_roadmaps/{collectionIndex}/fk_roadmap_task:destroy]()Destroy and disassociate the relationship record

**POST**[/personal_roadmaps/{collectionIndex}/fk_roadmap_task:set]()Set or reset associations

**POST**[/personal_roadmaps/{collectionIndex}/fk_roadmap_task:remove]()Detach record

**POST**[/personal_roadmaps/{collectionIndex}/fk_roadmap_task:toggle]()Attach or detach record


# Digiforce Open API Specs

API DOC PLUGIN

### [swagger]()

**GET**[/swagger:getUrls]()

Get all api-doc destination

#### Parameters

Try it out

No parameters

#### Responses

| Code | Description                                                                                      | Links |
| ---- | ------------------------------------------------------------------------------------------------ | ----- |
| 200  | successful operationMedia typeapplication/jsonControls `Accept` header.* Example Value* Schema |       |

```json
[
  {
"name": "string",
"url": "string"
  }
]
```

 |


### [workflows]()Workflow management: CRUD, versioning, sync, manual execution

**GET**[/workflows:list]()List workflows

**GET**[/workflows:get]()Get single workflow

**POST**[/workflows:create]()Create new workflow

**POST**[/workflows:update]()Update a workflow

**POST**[/workflows:destroy]()Delete workflows

**POST**[/workflows:revision]()Duplicate a workflow (create a revision)

**POST**[/workflows:sync]()Sync workflow trigger registration

**POST**[/workflows:execute]()Manually execute a workflow

### [workflows.nodes]()Create nodes inside a workflow (association resource)

**POST**[/workflows/{workflowId}/nodes:create]()Create a node in a workflow

### [flow_nodes]()Flow node management: update, delete, move, duplicate, test

**GET**[/flow_nodes:get]()Get single node

**POST**[/flow_nodes:update]()Update node properties

**POST**[/flow_nodes:destroy]()Delete a node

**POST**[/flow_nodes:destroyBranch]()Delete a specific branch of a branching node

**POST**[/flow_nodes:duplicate]()Duplicate a node

**POST**[/flow_nodes:move]()Move a node to a different position

**POST**[/flow_nodes:test]()Test a node configuration

### [executions]()Execution record management: list, get, cancel, delete

**GET**[/executions:list]()List executions

**GET**[/executions:get]()Get single execution

**POST**[/executions:cancel]()Cancel a running execution

**POST**[/executions:destroy]()Delete execution records

### [jobs]()Node job management: list, get, resume

**GET**[/jobs:list]()List jobs

**GET**[/jobs:get]()Get single job

**POST**[/jobs:resume]()Resume execution via a job

### [userWorkflowTasks]()Current-user workflow task queries

**GET**[/userWorkflowTasks:listMine]()List my workflow tasks
