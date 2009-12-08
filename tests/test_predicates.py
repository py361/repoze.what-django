# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Unit tests for the Django-specific repoze.what predicates.

"""

from nose.tools import eq_

from repoze.what.predicates import NotAuthorizedError

from repoze.what.plugins.dj import (RepozeWhatMiddleware, is_staff, is_active,
                                    is_superuser)
from tests import Request, make_user


class BasePredicateTester(object):
    """Base test case for predicates."""
    
    def eval_met_predicate(self, p, environ):
        """Evaluate a predicate that should be met"""
        eq_(p.check_authorization(environ), None)
        eq_(p.is_met(environ), True)
    
    def eval_unmet_predicate(self, p, environ, expected_error):
        """Evaluate a predicate that should not be met"""
        credentials = environ.get('repoze.what.credentials', {})
        
        # Testing check_authorization
        try:
            p.evaluate(environ, credentials)
        except NotAuthorizedError, error:
            eq_(unicode(error), expected_error)
        else:
            raise AssertionError("Predicate must not be met; expected error: %s"
                                 % expected_error)
        
        # Testing is_met:
        eq_(p.is_met(environ), False)
    
    #{ Fixture
    
    def setUp(self):
        """Set up the request."""
        mw = RepozeWhatMiddleware()
        self.request = Request({}, make_user("foo"))
        mw.process_request(self.request)
    
    #}


class TestIsStaff(BasePredicateTester):
    """Tests for the :class:`is_staff` predicate."""
    
    def test_non_staff_user(self):
        """
        The predicate must not be met if the user doesn't belong to the staff.
        
        """
        self.request.user.is_staff = False
        self.eval_unmet_predicate(is_staff(), self.request.environ,
                                  "The current user must belong to the staff")
    
    def test_staff_user(self):
        """
        The predicate must be met if the user DOES belong to the staff.
        
        """
        self.request.user.is_staff = True
        self.eval_met_predicate(is_staff(), self.request.environ)


class TestIsActive(BasePredicateTester):
    """Tests for the :class:`is_active` predicate."""
    
    def test_inactive_account(self):
        """
        The predicate must not be met if the user's account is inactive.
        
        """
        self.request.user.is_active = False
        self.eval_unmet_predicate(
            is_active(),
            self.request.environ,
            "The account for the current user must be active",
            )
    
    def test_active_account(self):
        """
        The predicate must be met if the user's account is active.
        
        """
        self.request.user.is_active = True
        self.eval_met_predicate(is_active(), self.request.environ)


class TestIsSuperuser(BasePredicateTester):
    """Tests for the :class:`is_superuser` predicate."""
    
    def test_regular_user(self):
        """
        The predicate must not be met if the user is not admin.
        
        """
        self.request.user.is_superuser = False
        self.eval_unmet_predicate(
            is_superuser(),
            self.request.environ,
            "The current user must be a superuser",
            )
    
    def test_superuser_account(self):
        """
        The predicate must be met if the user is an admin.
        
        """
        self.request.user.is_superuser = True
        self.eval_met_predicate(is_superuser(), self.request.environ)
