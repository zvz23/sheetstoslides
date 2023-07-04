from googleapiclient.discovery import build

class Presentation:
    def __init__(self, creds, presentation_id):
        self.creds = creds
        self.slides_service = build('slides', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.presentation_id = presentation_id
        self.reqs = []

    def get_title(self):
        return self.slides_service.presentations().get(presentationId=self.presentation_id).execute()['title']
    def get_all_slides(self):
        return self.slides_service.presentations().get(presentationId=self.presentation_id
       ).execute().get('slides')
    
    def duplicate_slide(self, slide_id, count):
        for i in range(count - 1):
            self.reqs.append({
                'duplicateObject': {
                    'objectId': slide_id
                }
            })

    
    def replace_placholder_text(self, text, slide_id):
        reqs = [
            {'replaceAllText': {
                'containsText': {'text': '{{NAME}}'},
                'replaceText': text,
                'pageObjectIds': [slide_id]
            }}
        ]
        self.slides_service.presentations().batchUpdate(body={'requests': reqs},
        presentationId=self.presentation_id).execute()
    
    def replace_shapes_with_instagram(self, slide_id, instagram, submission_title):
        image_urls_format = f"LEFT IMAGE:\n {instagram['images'][0]}"
        slides = self.get_all_slides()
        notes_id = None
        for slide in slides:
            if slide['objectId'] == slide_id:
                notes_id = slide['slideProperties']['notesPage']['notesProperties']['speakerNotesObjectId']             
                for obj in slide['pageElements']:
                    if obj['shape']['shapeType'] == 'TEXT_BOX':
                        name = instagram['name'].strip()
                        name_parts = name.split(' ')
                        to_add_name = None
                        if len(name_parts) > 1:
                            to_add_name = ' '.join(name_parts[0:-1]) + f' {name_parts[-1][0]}.'
                        else:
                            to_add_name = name
                        name_last_index = len(to_add_name)
                        if submission_title and instagram['submission']:
                            submission_title = submission_title.strip()
                            to_add_name = f'{to_add_name} {submission_title}'
                        self.reqs.append({
                            'replaceAllText': {
                                'replaceText': f"{to_add_name}",
                                'pageObjectIds': [slide_id],
                                'containsText': {
                                    'text': '{{NAME}}',
                                    'matchCase': True
                                }
                            },

                        })
                        self.reqs.append({
                            'updateTextStyle': {
                                'objectId': obj['objectId'],
                                'textRange': {
                                    'type': 'FIXED_RANGE',
                                    'startIndex': 0,
                                    'endIndex': name_last_index
                                },
                                'style': {
                                    'link': {
                                        'url': instagram['instagram_url']
                                    }
                                },
                                'fields': 'link'
                            }
                        })
                        if submission_title and instagram['submission']:
                            self.reqs.append({
                            'updateTextStyle': {
                                'objectId': obj['objectId'],
                                'textRange': {
                                    'type': 'FIXED_RANGE',
                                    'startIndex': name_last_index + 1,
                                    'endIndex': len(to_add_name)
                                },
                                'style': {
                                    'link': {
                                        'url': instagram['submission']
                                    }
                                },
                                'fields': 'link'
                            }
                        })
                        break

        self.reqs.append({
            'replaceAllText': {
                'replaceText': instagram['name'],
                'pageObjectIds': [slide_id],
                'containsText': {
                    'text': '{{NAME}}',
                    'matchCase': True
                }
            }
        })
        if len(instagram['images']) > 0:
            self.reqs.append({
                'replaceAllShapesWithImage': {
                    'imageReplaceMethod': 'CENTER_CROP',
                    'pageObjectIds': [slide_id],
                    'imageUrl': instagram['images'][0],
                    'containsText': {
                        'text': '{{IMAGE1}}',
                        'matchCase': True
                    }
                }
            })
            if len(instagram['images']) > 1:
                self.reqs.append({
                'replaceAllShapesWithImage': {
                    'imageReplaceMethod': 'CENTER_CROP',
                    'pageObjectIds': [slide_id],
                    'imageUrl': instagram['images'][1],
                    'containsText': {
                        'text': '{{IMAGE2}}',
                        'matchCase': True
                    }
                }
            })
            image_urls_format = image_urls_format + f"\n\nRIGHT IMAGE:\n {instagram['images'][1]}"
        self.reqs.append({
            'insertText': {
                'objectId': notes_id,
                'text': image_urls_format
            }
        })

    def apply_reqs(self):
        if len(self.reqs) > 0:
            self.slides_service.presentations().batchUpdate(body={'requests': self.reqs},presentationId=self.presentation_id).execute()
            self.reqs.clear()

    def copy_this_presentation(self, title: str):
        rsp = self.drive_service.files().list(q=f"name='{self.get_title()}'" ).execute().get('files')[0]
        DATA = {'name': title}
        presentation_id = self.drive_service.files().copy(body=DATA, fileId=rsp['id']).execute().get('id')
        return Presentation(self.creds, presentation_id)
    
    def copy_presentation(creds, source_title: str, copy_title: str):
        drive_service = build('drive', 'v3', credentials=creds)
        rsp = drive_service.files().list(q=f"name='{source_title}'" ).execute().get('files')[0]
        DATA = {'name': copy_title}
        presentation_id = drive_service.files().copy(body=DATA, fileId=rsp['id']).execute().get('id')
        perm_req_body = {
            'role': 'reader',
            'type': 'user',
            'emailAddress': 'espritcasting@gmail.com'
        }
        drive_service.permissions().create(
            fileId=presentation_id,
            body=perm_req_body
        ).execute()


        return Presentation(creds, presentation_id)
    
    def replace_text(self, slide_id, image_url):
        reqs = [{
            'replaceAllShapesWithImage': {
                'imageReplaceMethod': 'CENTER_INSIDE',
                'pageObjectIds': [slide_id],
                'imageUrl': image_url,
                'containsText': {
                    'text': 'IMAGE2',
                    'matchCase': False
                }
            }
        }]
        self.slides_service.presentations().batchUpdate(body={'requests': reqs},presentationId=self.presentation_id).execute() 


    