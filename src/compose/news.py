# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load news."""

import logging
import os
from collections import UserDict

from config import News, Project

from hugo import Page


class NewsPage(Page):
    """News Hugo page."""

    @classmethod
    def from_config(cls, config: News) -> 'NewsPage':
        """
        Create a news page from a configuration.

        Parameters:
            config: News configuration.

        Returns:
            NewsPage: Instance of NewsPage class.
        """
        front_matter = config.model_dump(exclude_none=True)
        return cls(front_matter=front_matter, markdown=config.description)


class NewsSection(UserDict[str, NewsPage]):
    """News Hugo section."""

    @classmethod
    def from_config(cls, configs: list[Project]) -> 'NewsSection':
        """
        Create a news section from a list of configurations.

        Parameters:
            configs: Project configurations.

        Returns:
            NewsSection: Instance of NewsSection class.
        """
        news_section = {}
        for project in configs:
            try:
                news = project.news
            except ValueError as enumerate_error:
                logging.error("Failed to get news from '{0}':\n{1}".format(
                    project.id, enumerate_error,
                ))
                continue
            news_section.update(cls._from_config(news))
        return cls(news_section)

    def write(self, path: str) -> None:
        """
        Write the news section to files.

        Parameters:
            path: news content directory path.

        Raises:
            ValueError: If writing the news section to files fails.
        """
        try:
            os.makedirs(path)
        except OSError as makedirs_error:
            raise ValueError("Failed to create '{0}' directory:\n{1}".format(
                path, makedirs_error,
            ))
        for page, news in self.data.items():
            logging.info("Writing '{0}' page...".format(page))
            try:
                news.write(os.path.join(path, '{0}.md'.format(page)))
            except ValueError as write_error:
                logging.error("Failed to write '{0}' page:\n{1}".format(
                    page, write_error,
                ))

    @classmethod
    def _from_config(cls, config: list[News]):
        news_section = {}
        for index, news in enumerate(config):
            page = '{0}-{1}'.format(news.topics[0], index + 1)
            logging.info("Generating '{0}' page...".format(page))
            try:
                news_section[page] = NewsPage.from_config(news)
            except ValueError as news_error:
                logging.error("Failed to generate '{0}' page:\n{1}".format(
                    page, news_error,
                ))
        return news_section
