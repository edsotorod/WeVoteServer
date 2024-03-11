# apis_v1/test_views_voter_email_address_save.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-
# "pbkdf2_sha256$260000$qW5s241tYo0kg50o05pKDP$aALBlgi0AlELFzNwPpClH6FjtPsuml9f08/KBagcuoA="

from django.urls import reverse
from django.test import TestCase
from email_outbound.models import EmailAddress, EmailManager
import json


class WeVoteAPIsV1TestsVoterEmailAddressSave(TestCase):
    databases = ["default", "readonly"]

    def setUp(self):
        self.generate_voter_device_id_url = reverse("apis_v1:deviceIdGenerateView")
        self.voter_create_url = reverse("apis_v1:voterCreateView")
        self.voter_email_address_save_url = reverse("apis_v1:voterEmailAddressSaveView")
        self.voter_email_address_retrieve_url = reverse("apis_v1:voterEmailAddressRetrieveView")
        
    def test_save_with_no_voter_device_id(self):
        response = self.client.post(self.voter_email_address_save_url)
        json_data = json.loads(response.content.decode())
        
        #######################################
        # Without a cookie, we don't expect valid response
        self.assertEqual('status' in json_data, True, "status expected in the json response, and not found")
        self.assertEqual('voter_device_id' in json_data, True,
                         "voter_device_id expected in the voterEmailAddressSaveView json response, and not found")
        
        self.assertEqual(json_data['status'], 
                        "VOTER_EMAIL_ADDRESS_SAVE-START VALID_VOTER_DEVICE_ID_MISSING  VOTER_DEVICE_ID_NOT_VALID ",
            "status: {status} ('VOTER_EMAIL_ADDRESS_SAVE-START VALID_VOTER_DEVICE_ID_MISSING VOTER_DEVICE_ID_NOT_VALID' expected), "
            "voter_device_id: {voter_device_id}".format(status=json_data['status'], 
            voter_device_id=json_data['voter_device_id']))
            
    def test_save_with_voter_device_id(self):
        #######################################
        # Generate the voter_device_id cookie
        response = self.client.get(self.generate_voter_device_id_url)
        json_data = json.loads(response.content.decode())

        # Make sure we got back a voter_device_id we can use
        self.assertEqual('voter_device_id' in json_data, True,
                         "voter_device_id expected in the deviceIdGenerateView json response")
        
        # Now put the voter_device_id in a variable we can use below
        voter_device_id = json_data['voter_device_id'] if 'voter_device_id' in json_data else ''
        
        #######################################
        # Create a voter so we can test retrieve
        response2 = self.client.get(self.voter_create_url, {'voter_device_id': voter_device_id})
        json_data2 = json.loads(response2.content.decode())

        self.assertEqual('status' in json_data2, True,
                         "status expected in the voterEmailAddressSaveView json response but not found")
        self.assertEqual('voter_device_id' in json_data2, True,
                         "voter_device_id expected in the voterEmailAddressSaveView json response but not found")

        # With a brand new voter_device_id, a new voter record should be created
        self.assertEqual(
            json_data2['status'], 'VOTER_CREATED',
            "status: {status} (VOTER_CREATED expected in voterEmailAddressSaveView), "
            "voter_device_id: {voter_device_id}".format(
                status=json_data2['status'], voter_device_id=json_data2['voter_device_id']))

        #######################################
        # Create a voter email address so we can test retrieve
        response2 = self.client.get(self.voter_email_address_save_url, {'text_for_email_address':
                                                                  'test123@gmail.com',
                                                                  'voter_device_id': voter_device_id})

        json_data2 = json.loads(response2.content.decode())

        self.assertEqual('status' in json_data2, True,
                         "status expected in the voterEmailAddressSaveView json response but not found")
        self.assertEqual('voter_device_id' in json_data2, True,
                         "voter_device_id expected in the voterEmailAddressSaveView json response but not found")
        self.assertEqual('success' in json_data2, True,
                         "success expected in the voterEmailAddressSaveView json response but not found")
        self.assertEqual('text_for_email_address' in json_data2, True,
                         "address expected in the voterEmailAddressSaveView json response but not found")

        # First voter email address save
        self.assertEqual(json_data2['status'], 
                        "VOTER_EMAIL_ADDRESS_SAVE-START CREATE_NEW_EMAIL_ADDRESS EMAIL_ADDRESS_FOR_VOTER_CREATED EMAIL_ADDRESS_FOR_VOTER_CREATED EMAIL_OUTBOUND_DESCRIPTION_CREATED  SCHEDULE_EMAIL_CREATED  EMAIL_SCHEDULED ",
            "status: {status} ('VOTER_EMAIL_ADDRESS_SAVE-START CREATE_NEW_EMAIL_ADDRESS EMAIL_ADDRESS_FOR_VOTER_CREATED EMAIL_ADDRESS_FOR_VOTER_CREATED EMAIL_OUTBOUND_DESCRIPTION_CREATED  SCHEDULE_EMAIL_CREATED  EMAIL_SCHEDULED ' expected), "
            "voter_device_id: {voter_device_id}".format(status=json_data2['status'], 
            voter_device_id=json_data2['voter_device_id']))
            
        # Try and save the voter email address again
        response3 = self.client.get(self.voter_email_address_save_url, {'text_for_email_address':
                                                                  'test321@gmail.com',
                                                                  'voter_device_id': voter_device_id})

        json_data3 = json.loads(response3.content.decode())
        
        self.assertEqual(json_data3['status'], 
                        "VOTER_EMAIL_ADDRESS_SAVE-START CREATE_NEW_EMAIL_ADDRESS EMAIL_ADDRESS_FOR_VOTER_CREATED EMAIL_ADDRESS_FOR_VOTER_CREATED EMAIL_OUTBOUND_DESCRIPTION_CREATED  SCHEDULE_EMAIL_CREATED  EMAIL_SCHEDULED ",
            "status: {status} ('VOTER_EMAIL_ADDRESS_SAVE-START CREATE_NEW_EMAIL_ADDRESS EMAIL_ADDRESS_FOR_VOTER_CREATED EMAIL_ADDRESS_FOR_VOTER_CREATED EMAIL_OUTBOUND_DESCRIPTION_CREATED  SCHEDULE_EMAIL_CREATED  EMAIL_SCHEDULED ' expected), "
            "voter_device_id: {voter_device_id}".format(status=json_data3['status'], 
            voter_device_id=json_data3['voter_device_id']))
         
        ######################################################################    
        # Test to make sure the email address has been saved in the database
        response4 = self.client.get(self.voter_email_address_retrieve_url, {'voter_device_id': voter_device_id})
        json_data4 = json.loads(response4.content.decode())

        # Are any expected fields missing?
        self.assertEqual('status' in json_data4, True,
                         "status expected in the voterEmailAddressSaveView json response but not found")
        self.assertEqual('voter_device_id' in json_data4, True,
                         "voter_device_id expected in the voterEmailAddressSaveView json response but not found")
        self.assertEqual('success' in json_data4, True,
                         "success expected in the voterEmailAddressSaveView json response but not found")
        self.assertEqual('email_address_list' in json_data4, True,
                         "email_address_list expected in the voterEmailAddressSaveView json response but not found")
        # A more thorough testing of expected variables is done in test_views_voter_email_address_retrieve.py

        # Confirm that we have two email addresses for this user
        self.assertEqual(
            len(json_data4['email_address_list']), 2, 
            "Length of email_address_list:{email_address_list_length} (expected to be 2), "
            "voter_device_id: {voter_device_id}".format(
                email_address_list_length=len(json_data4['email_address_list']), voter_device_id=json_data4['voter_device_id']))
        
        ######################################################################
        # Now try to save an invalid email address
        response5 = self.client.get(self.voter_email_address_save_url, {'text_for_email_address':
                                                                  'test321gmail.com',
                                                                  'voter_device_id': voter_device_id})

        json_data5 = json.loads(response5.content.decode())
        
        self.assertEqual(json_data5['status'], 
                        "VOTER_EMAIL_ADDRESS_SAVE-START VOTER_EMAIL_ADDRESS_SAVE_MISSING_VALID_EMAIL ",
            "status: {status} ('VOTER_EMAIL_ADDRESS_SAVE-START VOTER_EMAIL_ADDRESS_SAVE_MISSING_VALID_EMAIL ' expected), "
            "voter_device_id: {voter_device_id}".format(status=json_data5['status'], 
            voter_device_id=json_data5['voter_device_id']))
        
        self.assertEqual(json_data5['email_address_not_valid'], 
                        True,
            "email_address_not_valid: {email_address_not_valid} ('True' expected), "
            "voter_device_id: {voter_device_id}".format(email_address_not_valid=json_data5['email_address_not_valid'],
            voter_device_id=json_data5['voter_device_id']))